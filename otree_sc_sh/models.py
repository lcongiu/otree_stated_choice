from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)

import itertools
import random

author = 'Luca Congiu'

doc = """
oTree Module for Stated Choice Experiments.
************ 
Version 1.0.
************
Supports for:
- n° attributes = 3 
- n° levels >= 2
- n° options in choice set = 2
"""


class Constants(BaseConstants):

    # Settings
    # ---------------------------------------------------------------------------------------
    name_in_url = 'otree_sc_sh'
    players_per_group = None

    # Number of choice sets
    # N: The number of rounds must not exceed the number of choice sets to present
    # (see Terminal after starting a session to check both values).
    # If session fails to generate because "Sample larger than population or is negative" (ValueError),
    # lower the number of rounds (as indicated in Terminal)
    num_rounds = 6

    # Number of options for choice set
    # N: Please, do not touch this setting: the current release does not support higher values
    # TODO: support for 3 options per choice set
    optionsNumber = 2

    # Include "None" option
    # If True, choice sets will include a "None" option, allowing to reject both main options
    none_option = True

    # Attributes and levels to be packed into options
    # ---------------------------------------------------------------------------------------
    # Attributes
    # N: max number of attributes is 3
    # TODO: support for number of attributes higher than 3
    attributesList = 'Condizione', 'Garanzia', 'Prezzo',

    # Levels for each attribute
    # N: Levels must be ordered from best to worst
    # TODO: rating questions for subjective orderings
    levelsAttribute1 = 'Nuovo', 'Usato'
    levelsAttribute2 = 'Sì', 'No'
    levelsAttribute3 = '€50', '€100', '€150'

    levelsList = [
        levelsAttribute1, levelsAttribute2, levelsAttribute3
    ]

    attributesLevels = list(zip(attributesList, levelsList))


class Subsession(BaseSubsession):

    def creating_session(self):
        if self.round_number == 1:

            # Create choice sets
            # ---------------------------------------------------------------------------------------
            # Coding levels as numbers
            levelsDicts = []
            for l in range(len(Constants.levelsList)):
                codes = [c for c in range(1, len(Constants.levelsList[l]) + 1)]
                levelsDicts.append(dict(zip(codes, Constants.levelsList[l])))

            # Total pool of coded options
            optionsCodes = list(itertools.product(*levelsDicts))

            # Total choice sets (combinations of options)
            # ---------------------------------------------------------------------------------------
            choiceSets = list(itertools.combinations(optionsCodes, Constants.optionsNumber))

            # Dropping "non-informative" choice sets
            # N: Choice sets are kept if:
            # 1) all but two attributes are fixed (i.e. have same level in each option of the set)
            # 2) one attribute has a better (worse) level and the other has a worse (better) one
            # ---------------------------------------------------------------------------------------
            sets = []
            equality = []
            inequality = []

            for cs in range(len(choiceSets)):
                sets.append(cs)
                for l in range(len(choiceSets[cs][0])):
                    equality.append(choiceSets[cs][0][l] == choiceSets[cs][1][l])
                    inequality.append(choiceSets[cs][0][l] < choiceSets[cs][1][l])

            equality = [equality[i:i + len(Constants.levelsList)] for i in range(0, len(equality), len(Constants.levelsList))]
            inequality = [inequality[i:i + len(Constants.levelsList)] for i in range(0, len(inequality), len(Constants.levelsList))]
            comparisons = list(zip(sets, equality, inequality))

            # Creating final sample of coded options
            # ---------------------------------------------------------------------------------------
            choiceSetsSample = []

            for i in range(len(comparisons)):
                if comparisons[i][1].count(True) == 1:
                    if comparisons[i][2].count(True) == 1:
                        choiceSetsSample.append(choiceSets[i])

            # Check if num_rounds is lower than or equal to choiceSetsSample
            # ---------------------------------------------------------------------------------------
            print(f"*******\nA set of {len(choiceSetsSample)} choice sets was constructed. "
                  f"Constants.num_rounds cannot exceed {len(choiceSetsSample)}.")

            if len(choiceSetsSample) < Constants.num_rounds:
                print(f"*******\nWARNING:\nNumber of rounds exceeds number of selected choice sets."
                      f"Please, consider lowering the number of rounds to {len(choiceSetsSample)} or less.")


            # Random selection of options
            # ---------------------------------------------------------------------------------------
            choiceSetsSample = random.sample(choiceSetsSample, Constants.num_rounds)
            choiceSetsCoded = choiceSetsSample
            print(f"*******\nConstants.num_rounds is set to {Constants.num_rounds}. "
                  f"A sample of {len(choiceSetsSample)} choice sets was selected.")

            # Recoding options to original versions (with verbal levels)
            # ---------------------------------------------------------------------------------------
            # Create list of options with coded levels
            optionsCodedList = []

            for row in choiceSetsSample:
                for op in row:
                    optionsCodedList.append(list(op))

            optionsCoded = [optionsCodedList[i:i + 2] for i in range(0, len(optionsCodedList), 2)]

            # Substitute codes with corresponding verbal value
            for row in range(len(optionsCoded)):
                for op in range(len(optionsCoded[row])):
                    for lvl in range(len(optionsCoded[row][op])):
                        optionsCoded[row][op][lvl] = Constants.attributesLevels[lvl][1][int(optionsCoded[row][op][lvl]) - 1]

            # Pairing attributes with levels
            # ---------------------------------------------------------------------------------------
            optionsMatrix = []
            for option1, option2 in optionsCoded:
                for option in option1, option2:
                    optionsMatrix.append(list(zip(Constants.attributesList, option)))

            # Construct matrix of choice sets
            choiceSetsSample = [optionsMatrix[i:i + 2] for i in range(0, len(optionsMatrix), 2)]

            # Construct list of choice sets with indices
            indices = [i for i in range(1, len(choiceSetsSample[0]) + 1)]

            choiceSetsSampleIndex = []

            for k in range(len(choiceSetsSample)):
                choiceSetsSampleIndex.append(list(zip(indices, choiceSetsSample[k])))

            # Assign selected options to participants
            # ---------------------------------------------------------------------------------------
            for p in self.get_players():
                p.participant.vars['choice_sets'] = choiceSetsSample
                p.participant.vars['options'] = choiceSetsCoded
                p.participant.vars['options_index'] = choiceSetsSampleIndex
            #print(f"Choice sets for session: \n {choiceSetsSample}")
            #print(f"Choice sets for session (coded): \n {choiceSetsCoded}")
            print(f"*******\nFinal sample of choice sets for session:\n{choiceSetsSampleIndex}")

        # Assigning attributes and options as player fields
        # ---------------------------------------------------------------------------------------
        for p in self.get_players():
            p.attributes = str(Constants.attributesList)
            p.option1 = str(p.participant.vars['options'][self.round_number - 1][0])
            p.option2 = str(p.participant.vars['options'][self.round_number - 1][1])


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    attributes = models.StringField()
    option1 = models.StringField()
    option2 = models.StringField()

    choice = models.StringField()
