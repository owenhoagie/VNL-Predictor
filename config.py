# config.py
website_configs = [
    {
        "name": "blocking",
        "url": "https://en.volleyballworld.com/volleyball/competitions/men-world-championship/statistics/best-blockers/",
        "header_map": {
            "rank": "Rank",
            "playername": "Player Name",
            "federation": "Team",
            "stuff-blocks": "Blocks",
            "faults": "Blocking Errors",
            "rebounds": "Rebounds",
            "average-per-match": "Blocks Per Match",
            "success-perc": "Block Success %",
            "total-attempts": "Total Blocks"
        },
        "columns_to_keep": ["Player Name", "Team", "Blocks", "Blocking Errors", "Rebounds", "Blocks Per Match"]
    },
    {
        "name": "attacking",
        "url": "https://en.volleyballworld.com/volleyball/competitions/men-world-championship/statistics/best-attackers/",
        "header_map": {
            "rank": "Rank",
            "playername": "Player Name",
            "federation": "Team",
            "attacks": "Kills",
            "faults": "Attacking Errors",
            "shots": "Attacking Attempts",
            "average-per-match": "Attacks Per Match",
            "success-perc": "Attack Success %",
            "total-attempts": "Total Attack Attempts"
        },
        "columns_to_keep": ["Player Name", "Team", "Kills", "Attacking Errors", "Attack Attempts", "Attacks Per Match"]
    },
    {
        "name": "serving",
        "url": "https://en.volleyballworld.com/volleyball/competitions/men-world-championship/statistics/best-servers/",
        "header_map": {
            "rank": "Rank",
            "playername": "Player Name",
            "federation": "Team",
            "server-points": "Aces",
            "faults": "Service Errors",
            "hits": "Service Attempts",
            "average-per-match": "Serves Per Match",
            "success-perc": "Serve Success %",
            "total-attempts": "Total Serves"

        },
        "columns_to_keep": ["Player Name", "Team", "Aces", "Service Errors", "Service Attempts", "Serves Per Match"]
    },
    {
        "name": "setting",
        "url": "https://en.volleyballworld.com/volleyball/competitions/men-world-championship/statistics/best-setters/",
        "header_map": {
            "rank": "Rank",
            "playername": "Player Name",
            "federation": "Team",
            "running-sets": "Running Sets",
            "faults": "Setting Errors",
            "still-sets": "Still Sets",
            "average-per-match": "Sets Per Match",
            "success-perc": "Set Success %",
            "total-attempts": "Total Sets"
        },
        "columns_to_keep": ["Player Name", "Team", "Running Sets", "Setting Errors", "Still Sets", "Sets Per Match"]
    },
    {
        "name": "defense",
        "url": "https://en.volleyballworld.com/volleyball/competitions/men-world-championship/statistics/best-diggers/",
        "header_map": {
            "rank": "Rank",
            "playername": "Player Name",
            "federation": "Team",
            "great-save": "Great Saves",
            "faults": "Defensive Errors",
            "receptions": "Defensive Receptions",
            "average-per-match": "Digs Per Match",
            "success-perc": "Dig Success %",
            "total-attempts": "Total Digs"
        },
        "columns_to_keep": ["Player Name", "Team", "Great Saves", "Defensive Errors", "Receptions", "Digs Per Match"]
    },
    {
        "name": "receiving",
        "url": "https://en.volleyballworld.com/volleyball/competitions/men-world-championship/statistics/best-receivers/",
        "header_map": {
            "rank": "Rank",
            "playername": "Player Name",
            "federation": "Team",
            "excellents": "Successful Receives",
            "faults": "Receiving Errors",
            "serve-receptions": "Service Receptions",
            "average-per-match": "Receives Per Match",
            "success-perc": "Receive Success %",
            "total-attempts": "Total Receives"
        },
        "columns_to_keep": ["Player Name", "Team", "Successful Receives", "Receiving Errors", "Service Receptions", "Receives Per Match"]
    }
]