from algo import RPOLforkey
from k8sManager import K8sManager
import numpy as np
from time import sleep
from utils import reset_env, exp
import json

task_mul = 1

with open('/home/caohch1/Downloads/Erms/AE/simple/paras.json') as f:
    paras = json.load(f)

task = paras['task']

if task == "login":
    task = 0 * task_mul
elif task == "recommendation":
    task = 1 * task_mul
else:
    task = 2 * task_mul


sla = {0*task_mul: paras['sla'][0], 1*task_mul: paras['sla'][0], 2*task_mul: paras['sla'][0]}
obj_cost = {0*task_mul: paras['obj_cost'][0], 1*task_mul: paras['obj_cost'][0], 2*task_mul: paras['obj_cost'][0]}
obj_hardCost = {0*task_mul: paras['obj_hardCost'][0], 1*task_mul: paras['obj_hardCost'][0], 2*task_mul: paras['obj_hardCost'][0]}

k8sManager = K8sManager("hotel-reserv")

repeats = paras["repeats"]
periods = paras["periods"]
rounds = paras["rounds"]

avg_regret = np.zeros(periods)
avg_cost = np.zeros(periods)
avg_hardCost = np.zeros(periods)


for j in range(repeats):
    reset_env(k8sManager)
    pod_grid = [np.array([i for i in range(30, 0, -1)])]
    model = RPOLforkey(pod_grid, 1, [], paras["pobo_paras"][0], paras["pobo_paras"][1], paras["pobo_paras"][2], paras["pobo_paras"][3])
    regret_sum = []
    cost_sum = []
    hardCost_sum = []

    for i in range(periods):
        print("="*100)
        # Make decision
        # task = np.random.randint(0, task_num) * task_mul
        pod_num = int(model.decision(0)[-1])

        # Execute action
        if task == 0*task_mul:
            module_name = "login"
            k8sManager.scale_deployment("frontend", pod_num)
            k8sManager.scale_deployment("user", pod_num)
        elif task == 1*task_mul:
            module_name = "recommendation"
            k8sManager.scale_deployment("frontend", pod_num)
            k8sManager.scale_deployment("recommendation", pod_num)
            k8sManager.scale_deployment("profile", pod_num)
        elif task == 2*task_mul:
            module_name = "search"
            k8sManager.scale_deployment("frontend", pod_num)
            k8sManager.scale_deployment("search", pod_num)
            k8sManager.scale_deployment("rate", pod_num)
            k8sManager.scale_deployment("geo", pod_num)
            k8sManager.scale_deployment("profile", pod_num)
            k8sManager.scale_deployment("reservation", pod_num)

        # Repeat to get average latency, better experiment result
        sv_sum = []
        ul_sum = []
        for j in range(rounds):
            st, alj, svn, sv, sl, ul, cu, mu = exp(
                25, module_name, "30s", sla[task]*1000)
            if alj == 0 or ul == 0:
                continue
            sv_sum.append(sv)
            ul_sum.append(ul)
            sleep(2.5)

        sv = sum(sv_sum)/(len(sv_sum))
        ul = sum(ul_sum)/(len(ul_sum))
        ul /= 1000

        # Update model
        hardCost = ul
        reward = 100 - pod_num
        cost = sv
        model.update(reward, cost-obj_cost[task],
                            hardCost-obj_hardCost[task], 0)

        real_cost = cost
        hard_cost = hardCost
        regret = 100 - reward

        regret_sum.append(regret + regret_sum[-1] if regret_sum else regret)
        cost_sum.append(real_cost + cost_sum[-1] if cost_sum else real_cost)
        hardCost_sum.append(hard_cost + hardCost_sum[-1] if hardCost_sum else hard_cost)

        print(f"Period {i+1}: Pod Num.: {regret}, SLAV: {real_cost}, P90 TL: {hard_cost}")

    regret_sum = [regret_sum[i]/(i+1) for i in range(periods)]
    cost_sum = [cost_sum[i]/(i+1) for i in range(periods)]
    hardCost_sum = [hardCost_sum[i]/(i+1) for i in range(periods)]

    avg_regret += np.array(regret_sum)
    avg_cost += np.array(cost_sum)
    avg_hardCost += np.array(hardCost_sum)


avg_regret /= repeats
avg_cost /= repeats
avg_hardCost /= repeats
