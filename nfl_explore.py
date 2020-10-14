import pandas as pd

# Converts position string into tuple (isOpponent, position, rank)
# Ex1: "QB1" -> (False, "QB", 1)
# Ex2: "OppWR3" -> (True, "WR", 3)
def convertPos(posString):
    isOpponent = False
    if len(posString) > 3 and posString[0:3] == "Opp":
        isOpponent = True
        posString = posString[3:]
    pos = ""
    rnak = 0
    for c in posString:
        if c.isdigit():
            rank = int(c)
        else:
            pos += c
    return isOpponent, pos, rank

# Takes in a string of positions and get's those positions from the team and oppTeam dataframes
def getPosPlayers(teamData, oppTeamData, posStringList):
    result = pd.DataFrame()
    for posString in posStringList:
        isOpponent, pos, rank = convertPos(posString)
        if isOpponent:
            posData = oppTeamData[oppTeamData["Pos"] == pos].sort_values(by="DKSalary", ascending=False, ignore_index=True)
        else:
            posData = teamData[teamData["Pos"] == pos].sort_values(by="DKSalary", ascending=False, ignore_index=True)
        if len(posData) >= rank:
            player = posData.iloc[[rank - 1]]
        else:
            return None
        result = result.append(player)
    return result


# Takes in pandas df of players, and returns boolean of whether or not all of the players reach value
def doPlayersReachValue(players, valueMin):
    if players is None: return False
    fpSum = players["DK_Total_FP"].sum()
    salSum = players["DKSalary"].sum()
    return players is not None and salSum != 0 and ((fpSum / salSum) * 1000) > valueMin

# Gets the probability of a set of positions reaching valueMin (Total DKPoints/(Total DKSalary/1000))
def getValProb(asaDir, positions, valueMin):
    data = pd.read_csv(asaDir)
    data["Value"] = (data["DK_Total_FP"] / data["DKSalary"]) * 1000
    gameIDList = list(data["Game ID"].unique())
    valCount = 0
    gameCount = 0
    for gameID in gameIDList:
        homeData = data[(data["Game ID"] == gameID) & (data["H/A"] == "H")]
        awayData = data[(data["Game ID"] == gameID) & (data["H/A"] == "A")]
        if doPlayersReachValue(getPosPlayers(homeData, awayData, positions), valueMin):
            valCount += 1
        if doPlayersReachValue(getPosPlayers(awayData, homeData, positions), valueMin):
            valCount += 1
        gameCount += 2
    print(str(valCount) + "/" + str(gameCount))
    print(valCount / gameCount)

# Gets the conditional probability of all interestPositions reaching valueMin given that
# all givenPositions reached valueMin
def getValCondProb(asaDir, interestPositions, givenPositions, valueMin):
    data = pd.read_csv(asaDir)
    data["Value"] = (data["DK_Total_FP"] / data["DKSalary"]) * 1000
    gameIDList = list(data["Game ID"].unique())
    interestCount = 0
    givenCount = 0
    gameCount = 0
    for gameID in gameIDList:
        homeData = data[(data["Game ID"] == gameID) & (data["H/A"] == "H")]
        awayData = data[(data["Game ID"] == gameID) & (data["H/A"] == "A")]
        if doPlayersReachValue(getPosPlayers(homeData, awayData, interestPositions), valueMin) and \
                doPlayersReachValue(getPosPlayers(homeData, awayData, givenPositions), valueMin):
            interestCount += 1
            givenCount += 1
        elif doPlayersReachValue(getPosPlayers(homeData, awayData, givenPositions), valueMin):
            givenCount += 1
        if doPlayersReachValue(getPosPlayers(awayData, homeData, interestPositions), valueMin) and \
                doPlayersReachValue(getPosPlayers(awayData, homeData, givenPositions), valueMin):
            interestCount += 1
            givenCount += 1
        elif doPlayersReachValue(getPosPlayers(awayData, homeData, givenPositions), valueMin):
            givenCount += 1
        gameCount += 1
    print(str(interestCount) + "/" + str(givenCount))
    print(interestCount / givenCount)


# Prints the probability of games with Vegas O/U's between totalMin and totalMax reaching
# actualMin total points.
def vegasAverage(totalMin, totalMax, actualMin):
    data = pd.read_csv(asaDir)
    data["Actual Total"] = data["Team Score"] + data["Opponent Score"]
    totalData = data[(data["Over/Under"] >= totalMin) & (data["Over/Under"] <= totalMax)]
    minData = totalData[totalData["Actual Total"] >= actualMin]
    print(len(minData))
    print(len(totalData))
    print(len(minData) / len(totalData))


if __name__ == "__main__":
    # Example run comparing the probability of a WR2 reaching value given his QB, WR1, and the
    # opposing team's WR1 combined to reach value to the baseline probability for the WR2.
    asaDir = "ASA NFL Offense Raw Data 2015 - 2019.csv"
    getValCondProb(asaDir, ["WR2"], ["QB1", "WR1", "OppWR1"], 4)
    getValProb(asaDir, ["WR2"], 4)