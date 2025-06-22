from netqasm.sdk.classical_communication.socket import Socket
from netqasm.sdk.connection import BaseNetQASMConnection
from netqasm.sdk.epr_socket import EPRSocket
from netqasm.sdk.qubit import Qubit

from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta # type: ignore
from squidasm.util.routines import teleport_send, teleport_recv # type: ignore

import math
import random

prob_01 = 0.0#0.05
prob_10 = 0.0#0.005

class SenderProgram(Program):
    PEER_NAMES = ["Receiver0", "Receiver1"]
    def __init__(self, m, mu, l, faulty, **kwargs):
        super().__init__(**kwargs)
        self.m = m
        self.mu = mu
        self.l = l
        self.faulty = faulty

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="WBC",
            csockets=self.PEER_NAMES,
            epr_sockets=self.PEER_NAMES,
            max_qubits=10,
        )

    def run(self, context: ProgramContext):
        csockets: list[Socket] = [context.csockets[name] for name in self.PEER_NAMES]
        epr_sockets: list[EPRSocket] = [context.epr_sockets[name] for name in self.PEER_NAMES]
        connection: BaseNetQASMConnection = context.connection

        xs = random.choice([0, 1])
        if (self.faulty == "s"):
            csockets[0].send(0)
            csockets[1].send(1)
        else:
            if (self.faulty == "r0"):
                xs = 0
            csockets[0].send(xs)
            csockets[1].send(xs)

        csockets[0].send(f"{self.mu},{self.l}")
        csockets[1].send(f"{self.mu},{self.l}")

        csockets[0].send(self.m)
        csockets[1].send(self.m)

        measurements = []
        for i in range(self.m): 
            #Initialize qubits
            q0 = Qubit(connection)
            q1 = Qubit(connection)
            q2 = Qubit(connection)
            q3 = Qubit(connection)

            #Apply Loop Circuit from section 5.1 of the paper
            q0.H()
            q1.H()
            q2.H()

            q0.rot_Z(angle=-0.73304)
            q2.rot_Z(angle=2.67908)

            q2.cnot(q0)

            q0.rot_Y(angle=-2.67908)
            q2.H()

            q1.cnot(q0)
            q2.cnot(q3)

            q2.rot_Z(angle=1.5708)

            q1.cnot(q3)

            q0.cnot(q2)
            

            yield from teleport_send(q2, context, "Receiver0")
            yield from teleport_send(q3, context, "Receiver1")

            result = [q0.measure(), q1.measure()]
            yield from connection.flush()
            q0_m = result[0].value
            q1_m = result[1].value
            
            #Flip bits with specified probabilities (measurement error)
            # if (q0_m == 0):
            #     if (random.random() <= prob_01):
            #         q0_m = 1
            # else:
            #     if (random.random() <= prob_10):
            #         q0_m = 0

            # if (q1_m == 0):
            #     if (random.random() <= prob_01):
            #         q1_m = 1
            # else:
            #     if (random.random() <= prob_10):
            #         q1_m = 0
            measurements.append([q0_m, q1_m])

        if (self.faulty == "s"):
            check_set_0 = []
            check_set_1 = []
            T = math.ceil(self.mu*self.m)
            Q = T - math.ceil(self.l*T) + 1
            l1 = 0
            l2 = 0
            l3 = 0
            for values in measurements:
                if values[0] == 0 and values[1] == 0:
                    l1 += 1
                elif (values[0] != values[1]):
                    l2 += 1
                else:
                    l3 += 1
            
            if (T - Q > l1) or (Q > l2) or (T > l3):
               csockets[0].send([])
               csockets[1].send([])
               return {"ys": None}

            k_0011 = 0
            k_mixed = 0
            k_1100 = 0
            for i, values in enumerate(measurements):
                if values[0] == 0 and values[1] == 0:
                    if (k_0011 < T - Q):
                        check_set_0.append(i)
                        k_0011 += 1

                if values[0] != values[1]:
                    if (k_mixed < Q):
                        check_set_0.append(i)
                        k_mixed += 1

                if values[0] == 1 and values[1] == 1:
                    if (k_1100 < l3):
                        check_set_1.append(i)
                        k_1100 += 1

            csockets[0].send(check_set_0)
            csockets[1].send(check_set_1)
            return {"ys": xs}

        check_set = []
        for i, values in enumerate(measurements):
            if values[0] == xs and values[1] == xs:
                check_set.append(i)
        csockets[0].send(check_set)
        csockets[1].send(check_set)

        return {"ys": xs}


class Receiver0Program(Program):
    PEER_NAMES = ["Sender", "Receiver1"]
    def __init__(self, faulty, **kwargs):
        super().__init__(**kwargs)
        self.faulty = faulty

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="WBC",
            csockets=self.PEER_NAMES,
            epr_sockets=self.PEER_NAMES,
            max_qubits=10,
        )

    def run(self, context: ProgramContext):
        csockets: list[Socket] = [context.csockets[name] for name in self.PEER_NAMES]
        epr_sockets: list[EPRSocket] = [context.epr_sockets[name] for name in self.PEER_NAMES]
        connection: BaseNetQASMConnection = context.connection

        X0 = yield from csockets[0].recv()
        x0 = int(X0)

        mu_l = yield from csockets[0].recv()
        mu, l = [float(x) for x in mu_l.split(',')]

        M = yield from csockets[0].recv()
        m = int(M)

        measurements = []        
        for i in range(m):
            q = yield from teleport_recv(context, "Sender")
            result = q.measure()
            yield from connection.flush()
            q_m = result.value

            #Flip bit with specified probabilities (measurement error)
            # if (q_m == 0):
            #     if (random.random() <= prob_01):
            #         q_m = 1
            # else:
            #     if (random.random() <= prob_10):
            #         q_m = 0
            measurements.append(q_m)

        check_set = yield from csockets[0].recv()


        y0 = x0
        T = math.ceil(mu*m)
        if (self.faulty == "r0"):
            l1 = 0
            l2 = 0
            for i, value in enumerate(measurements):
                if value == 1:
                    if i in check_set:
                        l1 += 1
                    else:
                        l2 += 1
            if l1 > m - T:
                csockets[1].send(y0)
                csockets[1].send(check_set)
                return {"y0": None}
            y0 = 1
            new_check_set = []
            k_xx10 = 0
            k_xx0x = 0
            n_min = T - l2 if l2 < T else 0
            for i, value in enumerate(measurements):
                if (value == 1 and i not in check_set):
                    if (k_xx10 < l2):
                        new_check_set.append(i)
                        k_xx10 += 1
                elif (value == 0):
                    if (k_xx0x < n_min):
                        new_check_set.append(i)
                        k_xx0x += 1
            check_set = new_check_set
        else:
            if (len(check_set) < T):
                y0 = None

            for i in check_set:
                if (measurements[i] == x0):
                    y0 = None

        csockets[1].send(y0)
        csockets[1].send(check_set)

        return {"y0": y0}
    
class Receiver1Program(Program):
    PEER_NAMES = ["Sender", "Receiver0"]

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="WBC",
            csockets=self.PEER_NAMES,
            epr_sockets=self.PEER_NAMES,
            max_qubits=10,
        )

    def run(self, context: ProgramContext):
        csockets: list[Socket] = [context.csockets[name] for name in self.PEER_NAMES]
        epr_sockets: list[EPRSocket] = [context.epr_sockets[name] for name in self.PEER_NAMES]
        connection: BaseNetQASMConnection = context.connection

        X1 = yield from csockets[0].recv()
        x1 = int(X1)

        mu_l = yield from csockets[0].recv()
        mu, l = [float(x) for x in mu_l.split(',')]

        M = yield from csockets[0].recv()
        m = int(M)

        measurements = []        
        for i in range(m):
            q = yield from teleport_recv(context, "Sender")
            result = q.measure()
            yield from connection.flush()
            q_m = result.value

            #Flip bit with specified probabilities (measurement error)
            # if (q_m == 0):
            #     if (random.random() <= prob_01):
            #         q_m = 1
            # else:
            #     if (random.random() <= prob_10):
            #         q_m = 0
            measurements.append(q_m)

        check_set = yield from csockets[0].recv()

        y1_temp = x1

        T = math.ceil(mu*m)
        if (len(check_set) < T):
            y1_temp = None

        for i in check_set:
            if (measurements[i] == x1):
                y1_temp = None

        y0 = yield from csockets[1].recv()
        check_set_0 = yield from csockets[1].recv()

        y1 = y0

        if (len(check_set_0) < T or y0 is None or y1_temp is None):
            y1 = y1_temp
        else:
            y0 = int(y0)
            y1_temp = int(y1_temp)
            if (y0 == y1_temp):
                y1 = y1_temp
            else:
                num_opposite = 0
                for i in check_set_0:
                    if (measurements[i] != y0):
                        num_opposite += 1
                if (num_opposite < (l*T + len(check_set_0) - T)):
                    y1 = y1_temp

        return {"y1": y1}
