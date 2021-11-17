from builtins import range
from past.utils import old_div
import json
import sys
import time
from collections import namedtuple
from operator import add
import numpy as np


class BasicBot:
    """BasicBot will be given an AgentHost in its run method and just track down & attack various enemies"""
    def __init__(self, agent_host):
        self.obs_size = 30
        self.agent_host = agent_host
        return


    def get_observation(self, world_state):
        """
        Use the agent observation API to get a flattened 2 x 30 x 30 grid around the agent.
        The agent is in the center square facing up.

        Args
            world_state: <object> current agent world state

        Returns
            observation: <np.array> the state observation
        """
        obs = np.zeros((2 * self.obs_size * self.obs_size, ))

        while world_state.is_mission_running:
            time.sleep(0.1)
            world_state = self.agent_host.getWorldState()
            if len(world_state.errors) > 0:
                raise AssertionError('Could not load grid.')

            if world_state.number_of_observations_since_last_state > 0:
                # First we get the json from the observation API
                msg = world_state.observations[-1].text
                observations = json.loads(msg)
                if 'floorAll' not in observations:
                    continue
                # Get observation
                grid = observations['floorAll']

                # Rotate observation with orientation of agent
                obs = obs.reshape((2, self.obs_size, self.obs_size))
                yaw = observations['Yaw']
                if yaw >= 225 and yaw < 315:
                    obs = np.rot90(obs, k=1, axes=(1, 2))
                elif yaw >= 315 or yaw < 45:
                    obs = np.rot90(obs, k=2, axes=(1, 2))
                elif yaw >= 45 and yaw < 135:
                    obs = np.rot90(obs, k=3, axes=(1, 2))
                # obs = obs.flatten()

                break

        return obs


    def step(self):
        time.sleep(0.1)
        world_state = self.agent_host.getWorldState()
        if world_state.number_of_observations_since_last_state > 0:
            msg = world_state.observations[-1].text
            ob = json.loads(msg)
            '''Obs has the following keys:
            ['PlayersKilled', 'TotalTime', 'Life', 'ZPos', 'IsAlive',
            'Name', 'entities', 'DamageTaken', 'Food', 'Yaw', 'TimeAlive',
            'XPos', 'WorldTime', 'Air', 'DistanceTravelled', 'Score', 'YPos',
            'Pitch', 'MobsKilled', 'XP']
            '''
            # print("??")
            grid = self.get_observation(world_state)
            # print(ob['entities'], ob['XPos'], ob['YPos'])

            xPos = ob['XPos']
            yPos = ob['YPos']
            zPos = ob['ZPos']
            yaw = ob['Yaw']
            pitch = ob['Pitch']
            target = self.getNextTarget(ob['entities'])


            print(target)

            if target == None: # No enemies nearby
                if target != None:
                    sys.stdout.write("Not found: "+target['name'] + "\n")
                self.agent_host.sendCommand("move 0") # stop moving
                self.agent_host.sendCommand("attack 0") # stop attacking
                self.agent_host.sendCommand("turn 0") # stop turning
                self.agent_host.sendCommand("pitch 0") # stop looking up/down
            else:# enemy nearby, kill kill kill
                deltaYaw = 5
                deltaPitch = 5
                self.agent_host.sendCommand("turn " + str(deltaYaw))
                self.agent_host.sendCommand("pitch " + str(deltaPitch))
                self.agent_host.sendCommand("attack 1")

        for error in world_state.errors:
            print("Error:", error.text)

    def run(self, agent_host):
        """ Run the Agent on the world """
        agent_host.sendCommand("move 0.25")
        world_state = agent_host.getWorldState()
        while world_state.is_mission_running:
            #sys.stdout.write("*")
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
            if world_state.number_of_observations_since_last_state > 0:
                msg = world_state.observations[-1].text
                ob = json.loads(msg)
                '''Obs has the following keys:
                ['PlayersKilled', 'TotalTime', 'Life', 'ZPos', 'IsAlive',
                'Name', 'entities', 'DamageTaken', 'Food', 'Yaw', 'TimeAlive',
                'XPos', 'WorldTime', 'Air', 'DistanceTravelled', 'Score', 'YPos',
                'Pitch', 'MobsKilled', 'XP']
                '''
                # print(ob.keys())

                xPos = ob['XPos']
                yPos = ob['YPos']
                zPos = ob['ZPos']
                yaw = ob['Yaw']
                pitch = ob['Pitch']
                target = self.getNextTarget(ob['entities'])

                if target == None: # No enemies nearby
                    if target != None:
                        sys.stdout.write("Not found: "+target['name'] + "\n")
                    agent_host.sendCommand("move 0") # stop moving
                    agent_host.sendCommand("attack 0") # stop attacking
                    agent_host.sendCommand("turn 0") # stop turning
                    agent_host.sendCommand("pitch 0") # stop looking up/down
                else:# enemy nearby, kill kill kill
                    deltaYaw = 5
                    deltaPitch = 5
                    agent_host.sendCommand("turn " + str(deltaYaw))
                    agent_host.sendCommand("pitch " + str(deltaPitch))
                    agent_host.sendCommand("attack 1")

            for error in world_state.errors:
                print("Error:", error.text)

    def getNextTarget(self, entities):
        for entity in entities:
            if entity['name'] != "MurderBot":
                return entity

    '''
    To Be Done:
        Discretize distance, player health, and current_weapon into states:
            Distance (melee, close, far), Health (<10%, 10-60%, 60-100%), current_weapon (sword, bow)
        Add a state for EnemyType in the Specialist
    '''
