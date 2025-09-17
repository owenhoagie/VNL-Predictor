# config.py
website_configs = [
    {
        "name": "blocking",
        "url": "https://en.volleyballworld.com/volleyball/competitions/men-world-championship/statistics/best-blockers/",
        "header_map": {
            "playername": "Player Name",
            "federation": "Team",
            "stuff-blocks": "Blocks",
            "faults": "Blocking Errors",
            "rebounds": "Rebounds",
            "average-per-match": "Blocks Per Match"
        },
        "columns_to_keep": ["Player Name", "Team", "Blocks", "Blocking Errors", "Rebounds", "Blocks Per Match"]
    },
    {
        "name": "attacking",
        "url": "https://en.volleyballworld.com/volleyball/competitions/men-world-championship/statistics/best-attackers/",
        "header_map": {
            "playername": "Player Name",
            "federation": "Team",
            "attacks": "Kills",
            "faults": "Attacking Errors",
            "shots": "Attack Attempts",
            "average-per-match": "Attacks Per Match",
            "success-perc": "Attack Success %",
            "total-attempts": "Total Attack Attempts"
        },
        "columns_to_keep": ["Player Name", "Team", "Kills", "Attacking Errors", "Attack Attempts", "Attacks Per Match"]
    },
    # Add more websites here...
]