import pandas as pd
import numpy as np
from pulp import *
import time
import logging


logger = logging.getLogger('waitress')


def trigger_cbc_solver(sku_num, objective_metric, objective_threshold_flag, objective_threshold_value,
                       df_availability, df_requirement, df_objective):

    # Load Data
    tic = time.time()
    items_int = np.sort(df_availability['sku'].unique())
    sources_int = np.sort(df_availability['source'].unique())
    targets_int = np.sort(df_requirement['target'].unique())

    if objective_metric == 'cost':
        df_objective['cost_total'] = df_objective['cost_source'] + df_objective['cost_link'] + df_objective[
            'cost_target']

    if objective_metric == 'margin':
        df_objective['cost_total'] = df_objective['cost_upstream'] + df_objective['cost_source'] + df_objective[
            'cost_link'] + df_objective['cost_target']
        df_objective['margin'] = (df_objective['price_sale'] - df_objective['cost_total']) / df_objective[
            'price_sale']

    toc = time.time()
    load_duration = toc - tic

    # Initialise Nodes
    tic = time.time()
    items = list(map(str, items_int.tolist()))
    sources = list(map(str, sources_int.tolist()))
    targets = list(map(str, targets_int.tolist()))

    # Create List of Tuples Containing Arcs that Break Constraint
    if objective_metric == 'margin' and objective_threshold_value:
        if objective_threshold_flag == 1:
            df_breaking = df_objective[df_objective['margin'] < objective_threshold_value]
            df_breaking['sku'] = df_breaking['sku'].astype(str)
            df_breaking['source'] = df_breaking['source'].astype(str)
            df_breaking['target'] = df_breaking['target'].astype(str)
            breaking = []
            for index, row in df_breaking.iterrows():
                breaking.append((row['sku'], row['source'], row['target']))
    else:
        breaking = []

    # Create List of Tuples Containing All Possible Arcs
    df_availability['sku'] = df_availability['sku'].astype(str)
    df_availability['source'] = df_availability['source'].astype(str)
    df_requirement['sku'] = df_requirement['sku'].astype(str)
    df_requirement['target'] = df_requirement['target'].astype(str)
    arcs = []
    for i in items:
        for s in sources:
            for t in targets:
                arcs.append((i, s, t))

    # Create Dictionary to Capture Transportation Costs Along Different Arcs
    df_objective['source'] = df_objective['source'].astype(str)
    df_objective['target'] = df_objective['target'].astype(str)
    objective = []
    if 'sku' in df_objective.columns:
        df_objective['sku'] = df_objective['sku'].astype(str)
        for i in items:
            objective_source = []
            for s in sources:
                if objective_metric == 'cost':
                    objective_source.append(
                        df_objective[(df_objective['sku'] == i) & (df_objective['source'] == s)][
                            'cost_total'].tolist())
                elif objective_metric == 'margin':
                    objective_source.append(
                        df_objective[(df_objective['sku'] == i) & (df_objective['source'] == s)][
                            'margin'].tolist())
            objective.append(objective_source)
        objective = makeDict([items, sources, targets], objective, 0)
    else:
        if objective_metric == 'cost':
            for s in sources:
                objective.append(df_objective[df_objective['source'] == s]['cost_total'].tolist())
        objective = makeDict([sources, targets], objective, 0)

    # Create a Dictionary to Capture Source Availability
    availability = {i: d.groupby('source')['capacity'].mean().to_dict() for i, d in
                    df_availability.groupby('sku')}

    # Create a Dictionary to Capture Target Requirement
    requirement = {i: d.groupby('target')['demand'].mean().to_dict() for i, d in df_requirement.groupby('sku')}
    toc = time.time()
    network_variable_duration = toc - tic

    # Add Dummy Sources and Targets if Necessary
    tic = time.time()
    df_availability_group = df_availability.groupby('sku').sum()
    df_requirement_group = df_requirement.groupby('sku').sum()
    sku_shortfall = (df_availability_group['capacity'] - df_requirement_group['demand']).to_dict()

    if any(np.array(list(sku_shortfall.values())) < 0):
        sources.append("SX")
        for i in items:
            if sku_shortfall[i] < 0:
                availability[i]["SX"] = -sku_shortfall[i]
                for t in targets:
                    arcs.append((i, "SX", t))
            else:
                availability[i]["SX"] = 0

        objective_temp = len(targets) * [0]
        objective_temp = makeDict([targets], objective_temp, 0)
        if 'sku' in df_objective.columns:
            for i in items:
                objective[i]["SX"] = objective_temp
        else:
            objective["SX"] = objective_temp

    if any(np.array(list(sku_shortfall.values())) > 0):
        targets.append("TX")
        for i in items:
            if sku_shortfall[i] > 0:
                requirement[i]["TX"] = sku_shortfall[i]
                for s in sources:
                    arcs.append((i, s, "TX"))
            else:
                requirement[i]["TX"] = 0

        for s in sources:
            if 'sku' in df_objective.columns:
                for i in items:
                    objective[i][s]["TX"] = 0
            else:
                objective[s]["TX"] = 0

    toc = time.time()
    dummy_duration = toc - tic

    # Create 'prob' Variable to Contain Problem Data
    tic = time.time()
    if objective_metric == 'cost':
        prob = LpProblem("dynamic_allocation", LpMinimize)
    elif objective_metric == 'margin':
        prob = LpProblem("dynamic_allocation", LpMaximize)

    # Create Dictionary to Contain Arcs
    flow = LpVariable.dicts("Arc", (items, sources, targets), 0, None, LpInteger)
    toc = time.time()
    decision_variable_duration = toc - tic

    # Add Objective Function to 'prob'
    tic = time.time()
    if 'sku' in df_objective.columns:
        prob += (
            lpSum([flow[i][s][t] * objective[i][s][t] for (i, s, t) in arcs]),
            "sum_of_transportation_objectives",
        )
    else:
        prob += (
            lpSum([flow[i][s][t] * objective[s][t] for (i, s, t) in arcs]),
            "sum_of_transportation_objectives",
        )

    toc = time.time()
    objective_duration = toc - tic

    # Add Availability Constraints to 'prob'
    tic = time.time()
    for i in items:
        for s in sources:
            if s in availability[i]:
                prob += (
                    lpSum([flow[i][s][t] for t in targets]) == availability[i][s],
                    "sum_of_%s_units_leaving_sources_%s" % (i, s),
                )
            else:
                prob += (
                    lpSum([flow[i][s][t] for t in targets]) == 0,
                    "sum_of_%s_units_leaving_sources_%s" % (i, s),
                )

    # Add Requirement Constraints to 'prob'
    for i in items:
        for t in targets:
            if t in requirement[i]:
                prob += (
                    lpSum([flow[i][s][t] for s in sources]) == requirement[i][t],
                    "sum_of_%s_units_into_targets_%s" % (i, t),
                )
            else:
                prob += (
                    lpSum([flow[i][s][t] for s in sources]) == 0,
                    "sum_of_%s_units_into_targets_%s" % (i, t),
                )

    # Add Objective Threshold Constraints to 'prob'
    if (objective_metric == 'margin') & (objective_threshold_flag == 1):
        prob += lpSum([flow[i][s][t] for (i, s, t) in breaking]) == 0 # Number of units if a sku along breaking arc is 0

    toc = time.time()
    constraint_duration = toc - tic

    # Write the Data to an .lp File
    prob.writeLP("dynamic_allocation_problem.lp")

    # Solve
    tic = time.time()
    prob.solve()
    toc = time.time()

    solver_duration = toc - tic

    # Print Each Variable with its Resolved Optimum Value
    tic = time.time()
    rows = []
    if LpStatus[prob.status] == 'Optimal':
        for v in prob.variables():
            if v.varValue and v.varValue > 0:
                name = v.name.split('_')
                if name[2] == 'SX' or name[3] == 'TX':
                    is_SXTX = 1
                else:
                    is_SXTX = 0
                objective_row = df_objective.loc[(df_objective["sku"] == name[1]) &
                                              (df_objective["source"] == name[2]) &
                                              (df_objective["target"] == name[3]), ('margin',
                                                                                    'cost_upstream',
                                                                                    'cost_source',
                                                                                    'cost_link',
                                                                                    'cost_target',
                                                                                    'price_sale')]

                if is_SXTX:
                    arc_margin = 0
                    transfer_cost = 0
                    arc_total_cost = 0
                    arc_gross_profit = 0
                    price_sale = 0
                else:
                    arc_margin = objective_row['margin'].item()
                    transfer_cost = (objective_row['cost_source'].item() + objective_row['cost_link'].item() +
                                     objective_row['cost_target'].item()) * v.varValue
                    arc_total_cost = (objective_row['cost_source'].item() +
                                      objective_row['cost_link'].item() +
                                      objective_row['cost_target'].item() +
                                      objective_row['cost_upstream'].item()) * v.varValue
                    arc_gross_profit = objective_row['price_sale'].item() * v.varValue
                    price_sale = objective_row['price_sale'].item()

                rows.append([name[1], name[2], name[3], v.varValue, arc_margin, transfer_cost, arc_total_cost,
                             arc_gross_profit, price_sale, is_SXTX])
        results = pd.DataFrame(rows, columns=['sku', 'source', 'target', 'transfer', 'margin', 'transfer_cost',
                                              'arc_total_cost', 'arc_gross_profit', 'price_sale', 'is_sxtx'])
    else:
        logger.error("Problem Infeasible")
        results = []

    toc = time.time()
    write_duration = toc - tic
    vars_num = sku_num * len(sources) * len(targets)
    meta_data = {'number_of_variables': vars_num,
                 'loading_data': load_duration,
                 'creating_network_variables': network_variable_duration,
                 'creating_dummy_sources_and_targets': dummy_duration,
                 'creating_decision_variables': decision_variable_duration,
                 'creating_objective_function': objective_duration,
                 'adding_constraints': constraint_duration,
                 'solving_problem': solver_duration,
                 'writing_results': write_duration,
                 'total_duration': (load_duration + network_variable_duration + dummy_duration +
                                    decision_variable_duration + objective_duration + constraint_duration +
                                    solver_duration + write_duration)
                 }

    if objective_metric == 'cost':
        meta_data['solution'] = value(prob.objective)
    elif objective_metric == 'margin':
        if LpStatus[prob.status] == 'Optimal':
            solution = value(prob.objective) / results[results['is_sxtx'] == 0]['transfer'].sum()
            meta_data['solution'] = "Problem Optimized"
            meta_data['average_margin'] = (100 * solution)
            meta_data['transfer_cost'] = results['transfer_cost'].sum()
            meta_data['total_cost'] = results['arc_total_cost'].sum()
            meta_data['gross_profit'] = results['arc_gross_profit'].sum()
            results = results.to_dict('records')
        else:
            meta_data['solution'] = "Problem Infeasible"

    return {"dynamic_allocation": results, "solver_metadata": meta_data}

