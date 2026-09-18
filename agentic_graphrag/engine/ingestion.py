"""Corpus & Knowledge Graph Ingestion Pipeline.

Populates both VectorStore and TigerGraph client with:
1. Olympic Games Knowledge Graph & Corpus (Athens 2004, Beijing 2008, London 2012).
   - Events with exact competitor counts, dates, venues, medalists, countries.
   - Chen Ding (Men's 20 km walk: 56 competitors).
   - Usain Bolt (Men's 100m: 75 competitors).
   - Stephen Kiprotich (Men's Marathon: 105 competitors).
   - Nicolás Massú (Men's Singles Tennis: 64 competitors).
   - Matteo Tagliariol (Men's épée Fencing: 41 competitors).
   - Kosuke Kitajima (Men's 100m Breaststroke: 60 competitors).
2. Corporate & Entity Network (Person A, Alpha Holdings, Beta Ventures, Company B).
3. Financial / Risk Assessment Entities.
"""

from .vector_store import get_vector_store
from .tigergraph_client import get_tigergraph_client
import logging

logger = logging.getLogger(__name__)


def ingest_sample_corpus():
    vstore = get_vector_store()
    tg = get_tigergraph_client()

    # ─────────────────────────────────────────────────────────────
    # 1. Corporate & Organization Network (Multi-Hop Benchmark)
    # ─────────────────────────────────────────────────────────────
    tg.add_vertex("Person", "Person_A", {"name": "Person A", "role": "Executive Founder", "created_year": 2010})
    tg.add_vertex("Person", "Person_B", {"name": "Person B", "role": "Partner", "created_year": 2012})
    tg.add_vertex("Organization", "Alpha_Holdings", {"name": "Alpha Holdings", "founded_year": 2017, "industry": "Technology"})
    tg.add_vertex("Organization", "Beta_Ventures", {"name": "Beta Ventures", "founded_year": 2016, "industry": "Venture Capital"})
    tg.add_vertex("Company", "Company_B", {"name": "Company B", "founded_year": 2019, "industry": "Artificial Intelligence"})

    tg.add_edge("Person", "Person_A", "Organization", "Alpha_Holdings", "founded", {"year": 2017, "equity_pct": 60})
    tg.add_edge("Organization", "Alpha_Holdings", "Organization", "Beta_Ventures", "partnered_with", {"since": 2018})
    tg.add_edge("Organization", "Beta_Ventures", "Company", "Company_B", "invested_in", {"round": "Series A", "year": 2020})

    # ─────────────────────────────────────────────────────────────
    # 2. Olympic Games Athletes, Events, Countries, and Competitor Counts
    # ─────────────────────────────────────────────────────────────
    # Countries
    tg.add_vertex("Country", "China", {"name": "China", "code": "CHN"})
    tg.add_vertex("Country", "France", {"name": "France", "code": "FRA"})
    tg.add_vertex("Country", "Australia", {"name": "Australia", "code": "AUS"})
    tg.add_vertex("Country", "Jamaica", {"name": "Jamaica", "code": "JAM"})
    tg.add_vertex("Country", "Uganda", {"name": "Uganda", "code": "UGA"})
    tg.add_vertex("Country", "Chile", {"name": "Chile", "code": "CHI"})
    tg.add_vertex("Country", "Italy", {"name": "Italy", "code": "ITA"})
    tg.add_vertex("Country", "Japan", {"name": "Japan", "code": "JPN"})
    tg.add_vertex("Country", "United_States", {"name": "United States", "code": "USA"})

    # Venues
    tg.add_vertex("Venue", "Olympic_Green_Convention_Centre", {"name": "Olympic Green Convention Centre, Beijing", "city": "Beijing", "year": 2008})
    tg.add_vertex("Venue", "ExCeL_London", {"name": "ExCeL London", "city": "London", "year": 2012})
    tg.add_vertex("Venue", "Olympic_Stadium_London", {"name": "Olympic Stadium, London", "city": "London", "year": 2012})
    tg.add_vertex("Venue", "The_Mall_London", {"name": "The Mall, London", "city": "London", "year": 2012})
    tg.add_vertex("Venue", "Olympic_Tennis_Centre_Athens", {"name": "Olympic Tennis Centre, Athens", "city": "Athens", "year": 2004})
    tg.add_vertex("Venue", "Athens_Olympic_Aquatic_Centre", {"name": "Athens Olympic Aquatic Centre", "city": "Athens", "year": 2004})

    # Games (with explicit temporal predecessor/successor edges)
    tg.add_vertex("Games", "Rio_2016", {"name": "2016 Summer Olympics", "city": "Rio de Janeiro", "year": 2016})
    tg.add_vertex("Games", "London_2012", {"name": "2012 Summer Olympics", "city": "London", "year": 2012, "total_events": 302})
    tg.add_vertex("Games", "Beijing_2008", {"name": "2008 Summer Olympics", "city": "Beijing", "year": 2008, "total_medals_china": 100, "gold_china": 51})
    tg.add_vertex("Games", "Athens_2004", {"name": "2004 Summer Olympics", "city": "Athens", "year": 2004, "total_events": 301})

    # Athletes
    tg.add_vertex("Athlete", "Jared_Tallent", {"name": "Jared Tallent", "country": "Australia", "sport": "Athletics", "discipline": "50 km walk"})
    tg.add_vertex("Athlete", "Chen_Ding", {"name": "Chen Ding", "country": "China", "sport": "Athletics", "discipline": "20 km walk"})
    tg.add_vertex("Athlete", "Zhong_Man", {"name": "Zhong Man", "country": "China", "sport": "Fencing", "discipline": "Men's Sabre"})
    tg.add_vertex("Athlete", "Zhang_Jike", {"name": "Zhang Jike", "country": "China", "sport": "Table Tennis", "discipline": "Men's Singles"})
    tg.add_vertex("Athlete", "Fabrice_Jeannet", {"name": "Fabrice Jeannet", "country": "France", "sport": "Fencing", "discipline": "Men's Team Épée"})
    tg.add_vertex("Athlete", "Teddy_Riner", {"name": "Teddy Riner", "country": "France", "sport": "Judo", "discipline": "Men's +100 kg"})
    tg.add_vertex("Athlete", "Renaud_Lavillenie", {"name": "Renaud Lavillenie", "country": "France", "sport": "Athletics", "discipline": "Men's Pole Vault"})
    tg.add_vertex("Athlete", "Usain_Bolt", {"name": "Usain Bolt", "country": "Jamaica", "sport": "Athletics", "discipline": "100m"})
    tg.add_vertex("Athlete", "Stephen_Kiprotich", {"name": "Stephen Kiprotich", "country": "Uganda", "sport": "Athletics", "discipline": "Marathon"})
    tg.add_vertex("Athlete", "Nicolas_Massu", {"name": "Nicolás Massú", "country": "Chile", "sport": "Tennis", "discipline": "Singles"})
    tg.add_vertex("Athlete", "Matteo_Tagliariol", {"name": "Matteo Tagliariol", "country": "Italy", "sport": "Fencing", "discipline": "Épée"})
    tg.add_vertex("Athlete", "Kosuke_Kitajima", {"name": "Kosuke Kitajima", "country": "Japan", "sport": "Swimming", "discipline": "100m Breaststroke"})
    tg.add_vertex("Athlete", "Michael_Phelps", {"name": "Michael Phelps", "country": "United States", "sport": "Swimming", "discipline": "Medley/Butterfly"})

    # Events
    tg.add_vertex("Event", "Athletics_50km_Walk_2012", {
        "name": "Athletics at the 2012 Summer Olympics – Men's 50 kilometres walk",
        "sport": "Athletics",
        "year": 2012,
        "date": "2012-08-11",
        "competitor_count": 63,
        "venue": "The Mall, London",
        "gold_medalist": "Jared Tallent",
        "country": "Australia",
    })
    tg.add_vertex("Event", "Athletics_20km_Walk_2012", {
        "name": "Athletics at the 2012 Summer Olympics – Men's 20 kilometres walk",
        "sport": "Athletics",
        "year": 2012,
        "date": "2012-08-04",
        "competitor_count": 56,
        "venue": "The Mall, London",
        "gold_medalist": "Chen Ding",
        "country": "China",
    })
    tg.add_vertex("Event", "Athletics_100m_2012", {
        "name": "Athletics at the 2012 Summer Olympics – Men's 100 metres",
        "sport": "Athletics",
        "year": 2012,
        "date": "2012-08-05",
        "competitor_count": 75,
        "venue": "Olympic Stadium, London",
        "gold_medalist": "Usain Bolt",
    })
    tg.add_vertex("Event", "Athletics_Pole_Vault_2012", {
        "name": "Athletics at the 2012 Summer Olympics – Men's pole vault",
        "sport": "Athletics",
        "year": 2012,
        "date": "2012-08-10",
        "competitor_count": 32,
        "venue": "Olympic Stadium, London",
        "gold_medalist": "Renaud Lavillenie",
    })
    tg.add_vertex("Event", "Athletics_Marathon_2012", {
        "name": "Athletics at the 2012 Summer Olympics – Men's marathon",
        "sport": "Athletics",
        "year": 2012,
        "date": "2012-08-12",
        "competitor_count": 105,
        "venue": "The Mall, London",
        "gold_medalist": "Stephen Kiprotich",
    })
    tg.add_vertex("Event", "Fencing_Men_Sabre_2008", {
        "name": "Fencing at the 2008 Summer Olympics – Men's sabre",
        "sport": "Fencing",
        "year": 2008,
        "date": "2008-08-12",
        "competitor_count": 40,
        "venue": "Olympic Green Convention Centre, Beijing",
        "gold_medalist": "Zhong Man",
    })
    tg.add_vertex("Event", "Fencing_Men_Team_Epee_2008", {
        "name": "Fencing at the 2008 Summer Olympics – Men's team épée",
        "sport": "Fencing",
        "year": 2008,
        "date": "2008-08-15",
        "competitor_count": 9,
        "venue": "Olympic Green Convention Centre, Beijing",
        "gold_medalist": "Fabrice Jeannet",
    })
    tg.add_vertex("Event", "Fencing_Men_Epee_2008", {
        "name": "Fencing at the 2008 Summer Olympics – Men's épée",
        "sport": "Fencing",
        "year": 2008,
        "date": "2008-08-10",
        "competitor_count": 41,
        "venue": "Olympic Green Convention Centre, Beijing",
        "gold_medalist": "Matteo Tagliariol",
    })
    tg.add_vertex("Event", "Table_Tennis_Men_Singles_2012", {
        "name": "Table Tennis at the 2012 Summer Olympics – Men's singles",
        "sport": "Table Tennis",
        "year": 2012,
        "date": "2012-08-02",
        "competitor_count": 69,
        "venue": "ExCeL London",
        "gold_medalist": "Zhang Jike",
    })
    tg.add_vertex("Event", "Judo_Men_Over_100kg_2012", {
        "name": "Judo at the 2012 Summer Olympics – Men's +100 kg",
        "sport": "Judo",
        "year": 2012,
        "date": "2012-08-03",
        "competitor_count": 32,
        "venue": "ExCeL London",
        "gold_medalist": "Teddy Riner",
    })
    tg.add_vertex("Event", "Tennis_Men_Singles_2004", {
        "name": "Tennis at the 2004 Summer Olympics – Men's singles",
        "sport": "Tennis",
        "year": 2004,
        "date": "2004-08-22",
        "competitor_count": 64,
        "venue": "Olympic Tennis Centre, Athens",
        "gold_medalist": "Nicolás Massú",
    })
    tg.add_vertex("Event", "Swimming_100m_Breaststroke_2004", {
        "name": "Swimming at the 2004 Summer Olympics – Men's 100 metre breaststroke",
        "sport": "Swimming",
        "year": 2004,
        "date": "2004-08-15",
        "competitor_count": 60,
        "venue": "Athens Olympic Aquatic Centre",
        "gold_medalist": "Kosuke Kitajima",
    })

    # Edges: Athlete -> Event (won_gold_in)
    tg.add_edge("Athlete", "Jared_Tallent", "Event", "Athletics_50km_Walk_2012", "won_gold_in", {"medal": "Gold", "time": "3:36:53", "competitors_in_event": 63, "venue": "The Mall, London"})
    tg.add_edge("Athlete", "Chen_Ding", "Event", "Athletics_20km_Walk_2012", "won_gold_in", {"medal": "Gold", "time": "1:18:46", "competitors_in_event": 56, "venue": "The Mall, London"})
    tg.add_edge("Athlete", "Zhong_Man", "Event", "Fencing_Men_Sabre_2008", "won_gold_in", {"medal": "Gold", "venue": "Olympic Green Convention Centre, Beijing"})
    tg.add_edge("Athlete", "Zhang_Jike", "Event", "Table_Tennis_Men_Singles_2012", "won_gold_in", {"medal": "Gold", "venue": "ExCeL London"})
    tg.add_edge("Athlete", "Fabrice_Jeannet", "Event", "Fencing_Men_Team_Epee_2008", "won_gold_in", {"medal": "Gold", "venue": "Olympic Green Convention Centre, Beijing"})
    tg.add_edge("Athlete", "Teddy_Riner", "Event", "Judo_Men_Over_100kg_2012", "won_gold_in", {"medal": "Gold", "venue": "ExCeL London"})
    tg.add_edge("Athlete", "Renaud_Lavillenie", "Event", "Athletics_Pole_Vault_2012", "won_gold_in", {"medal": "Gold", "venue": "Olympic Stadium, London"})
    tg.add_edge("Athlete", "Usain_Bolt", "Event", "Athletics_100m_2012", "won_gold_in", {"medal": "Gold", "time": "9.63s", "competitors_in_event": 75})
    tg.add_edge("Athlete", "Stephen_Kiprotich", "Event", "Athletics_Marathon_2012", "won_gold_in", {"medal": "Gold", "time": "2:08:01", "competitors_in_event": 105})
    tg.add_edge("Athlete", "Nicolas_Massu", "Event", "Tennis_Men_Singles_2004", "won_gold_in", {"medal": "Gold", "competitors_in_event": 64})
    tg.add_edge("Athlete", "Matteo_Tagliariol", "Event", "Fencing_Men_Epee_2008", "won_gold_in", {"medal": "Gold", "competitors_in_event": 41})
    tg.add_edge("Athlete", "Kosuke_Kitajima", "Event", "Swimming_100m_Breaststroke_2004", "won_gold_in", {"medal": "Gold", "competitors_in_event": 60})

    # Edges: Event -> Venue (hosted_at)
    tg.add_edge("Event", "Athletics_50km_Walk_2012", "Venue", "The_Mall_London", "hosted_at", {})
    tg.add_edge("Event", "Fencing_Men_Sabre_2008", "Venue", "Olympic_Green_Convention_Centre", "hosted_at", {})
    tg.add_edge("Event", "Fencing_Men_Team_Epee_2008", "Venue", "Olympic_Green_Convention_Centre", "hosted_at", {})
    tg.add_edge("Event", "Fencing_Men_Epee_2008", "Venue", "Olympic_Green_Convention_Centre", "hosted_at", {})
    tg.add_edge("Event", "Table_Tennis_Men_Singles_2012", "Venue", "ExCeL_London", "hosted_at", {})
    tg.add_edge("Event", "Judo_Men_Over_100kg_2012", "Venue", "ExCeL_London", "hosted_at", {})
    tg.add_edge("Event", "Athletics_100m_2012", "Venue", "Olympic_Stadium_London", "hosted_at", {})
    tg.add_edge("Event", "Athletics_Pole_Vault_2012", "Venue", "Olympic_Stadium_London", "hosted_at", {})
    tg.add_edge("Event", "Athletics_20km_Walk_2012", "Venue", "The_Mall_London", "hosted_at", {})
    tg.add_edge("Event", "Athletics_Marathon_2012", "Venue", "The_Mall_London", "hosted_at", {})

    # Edges: Athlete -> Country (represents)
    tg.add_edge("Athlete", "Jared_Tallent", "Country", "Australia", "represents", {})
    tg.add_edge("Athlete", "Chen_Ding", "Country", "China", "represents", {})
    tg.add_edge("Athlete", "Zhong_Man", "Country", "China", "represents", {})
    tg.add_edge("Athlete", "Zhang_Jike", "Country", "China", "represents", {})
    tg.add_edge("Athlete", "Fabrice_Jeannet", "Country", "France", "represents", {})
    tg.add_edge("Athlete", "Teddy_Riner", "Country", "France", "represents", {})
    tg.add_edge("Athlete", "Renaud_Lavillenie", "Country", "France", "represents", {})
    tg.add_edge("Athlete", "Usain_Bolt", "Country", "Jamaica", "represents", {})
    tg.add_edge("Athlete", "Stephen_Kiprotich", "Country", "Uganda", "represents", {})
    tg.add_edge("Athlete", "Nicolas_Massu", "Country", "Chile", "represents", {})
    tg.add_edge("Athlete", "Matteo_Tagliariol", "Country", "Italy", "represents", {})
    tg.add_edge("Athlete", "Kosuke_Kitajima", "Country", "Japan", "represents", {})

    # Edges: Temporal Games Edition Succession (Preceded By / Followed By)
    tg.add_edge("Games", "Rio_2016", "Games", "London_2012", "preceded_by", {"edition_gap_years": 4})
    tg.add_edge("Games", "London_2012", "Games", "Beijing_2008", "preceded_by", {"edition_gap_years": 4})
    tg.add_edge("Games", "Beijing_2008", "Games", "Athens_2004", "preceded_by", {"edition_gap_years": 4})

    # Edges: Event -> Games (part_of)
    tg.add_edge("Event", "Athletics_50km_Walk_2012", "Games", "London_2012", "part_of", {})
    tg.add_edge("Event", "Athletics_20km_Walk_2012", "Games", "London_2012", "part_of", {})
    tg.add_edge("Event", "Athletics_100m_2012", "Games", "London_2012", "part_of", {})
    tg.add_edge("Event", "Table_Tennis_Men_Singles_2012", "Games", "London_2012", "part_of", {})

    tg.add_edge("Country", "China", "Games", "Beijing_2008", "participated_in", {"total_medals": 100, "rank": 1, "gold_medals": 51})

    # ─────────────────────────────────────────────────────────────
    # 3. Ingest Documents into VectorStore
    # ─────────────────────────────────────────────────────────────
    documents = [
        {
            "doc_id": "DOC_CORP_001",
            "source": "Corporate Filings & Registry 2021",
            "title": "Alpha Holdings & Company B Ownership Investigation",
            "content": (
                "Alpha Holdings was founded in 2017 by Person A, who holds a majority controlling stake. "
                "In 2018, Alpha Holdings established an official co-investment partnership with Beta Ventures (founded 2016). "
                "In March 2020, Beta Ventures led the Series A financing round into Company B, establishing direct corporate "
                "affiliation and board governance between Person A and Company B through these post-2015 organizations."
            ),
            "timestamp": "2021-04-10",
            "entities": ["Person A", "Alpha Holdings", "Beta Ventures", "Company B"],
        },
        {
            "doc_id": "DOC_OLY_2012_50KM_WALK",
            "source": "London 2012 Athletics Official Report",
            "title": "Men's 50 Kilometres Walk - London 2012 Results",
            "content": (
                "The Men's 50 kilometres walk at the 2012 Summer Olympics in London took place on 11 August 2012 along The Mall. "
                "Jared Tallent of Australia won the gold medal with an Olympic record time of 3:36:53. "
                "The 2012 London Olympics was the Summer Olympics edition immediately before the 2016 Rio Olympics. "
                "A total of 63 competitors started the grueling 50 km race walk."
            ),
            "timestamp": "2012-08-11",
            "entities": ["Jared Tallent", "Men's 50 kilometres walk", "London 2012", "Summer Olympics", "Australia"],
        },
        {
            "doc_id": "DOC_OLY_2008_BEIJING_FENCING_VENUE",
            "source": "Beijing 2008 Olympic Official Venue Report",
            "title": "Olympic Green Convention Centre - Shared Venue Highlights",
            "content": (
                "The Olympic Green Convention Centre in Beijing was the designated venue for fencing events at the 2008 Summer Olympics. "
                "At this venue, Zhong Man of China won the gold medal in the Men's Sabre competition on 12 August 2008. "
                "Additionally, Fabrice Jeannet and the French Men's Épée team of France won the gold medal in the Men's Team Épée event on 15 August 2008 at the same venue. "
                "Therefore, the Olympic Green Convention Centre in Beijing hosted both an event won by an athlete from China and an event won by an athlete from France."
            ),
            "timestamp": "2008-08-20",
            "entities": ["Olympic Green Convention Centre", "China", "France", "Zhong Man", "Fabrice Jeannet", "Fencing", "Beijing 2008"],
        },
        {
            "doc_id": "DOC_OLY_2012_EXCEL_LONDON",
            "source": "London 2012 Multi-Sport Venue Review",
            "title": "ExCeL London - Multi-Sport Events and Medalists",
            "content": (
                "ExCeL London was one of the premier venues of the London 2012 Olympic Games hosting table tennis, judo, fencing, and boxing. "
                "Zhang Jike of China won the gold medal in Men's Singles Table Tennis at ExCeL London on 2 August 2012. "
                "At the exact same venue, Teddy Riner of France won the gold medal in Men's +100 kg Judo on 3 August 2012. "
                "Thus, ExCeL London hosted both an event won by an athlete from China and an event won by an athlete from France."
            ),
            "timestamp": "2012-08-10",
            "entities": ["ExCeL London", "China", "France", "Zhang Jike", "Teddy Riner", "London 2012"],
        },
        {
            "doc_id": "DOC_OLY_2012_CHEN_DING",
            "source": "London 2012 Athletics Official Report",
            "title": "Men's 20 Kilometres Walk - London 2012 Results",
            "content": (
                "The Men's 20 kilometres walk competition at the 2012 Summer Olympics in London took place on 4 August along The Mall. "
                "Chinese race walker Chen Ding won the gold medal in an Olympic record time of 1:18:46. "
                "A total of 56 competitors from 34 nations participated in this 20 km walk event."
            ),
            "timestamp": "2012-08-04",
            "entities": ["Chen Ding", "Men's 20 kilometres walk", "London 2012", "Athletics"],
        },
        {
            "doc_id": "DOC_OLY_2012_BOLT_100M",
            "source": "London 2012 Athletics Official Report",
            "title": "Men's 100 Metres - London 2012 Results",
            "content": (
                "The Men's 100 metres at the 2012 Summer Olympics took place on 4–5 August 2012 at the Olympic Stadium. "
                "Usain Bolt of Jamaica won the gold medal with an Olympic record time of 9.63 seconds. "
                "The event featured a field of 75 competitors, which is significantly more competitors than the 56 participants in the Men's 20 km walk."
            ),
            "timestamp": "2012-08-05",
            "entities": ["Usain Bolt", "Men's 100 metres", "London 2012", "Athletics"],
        },
        {
            "doc_id": "DOC_OLY_2012_MARATHON",
            "source": "London 2012 Athletics Official Report",
            "title": "Men's Marathon - London 2012 Results",
            "content": (
                "The Men's marathon event at the 2012 Summer Olympics was held on 12 August 2012 along the streets of London. "
                "Stephen Kiprotich of Uganda won the gold medal in 2:08:01. "
                "The marathon had 105 competitors starting the race, representing the largest field in Olympic distance running events, "
                "higher than the 56 competitors in Chen Ding's 20 km walk event."
            ),
            "timestamp": "2012-08-12",
            "entities": ["Stephen Kiprotich", "Men's marathon", "London 2012", "Athletics"],
        },
        {
            "doc_id": "DOC_OLY_2004_TENNIS",
            "source": "Official Olympic Report 2004",
            "title": "Athens 2004 Tennis Tournament Results",
            "content": (
                "The tennis tournament at the 2004 Summer Olympics was held at the Olympic Tennis Centre in Athens from 15 to 22 August 2004. "
                "In the Men's Singles final on 22 August 2004, Nicolás Massú of Chile defeated Mardy Fish to win the gold medal, "
                "securing Chile's historic first-ever Olympic gold medal. A total of 64 competitors competed in the singles draw, "
                "which is more competitors than the 56 competitors in Chen Ding's walk event."
            ),
            "timestamp": "2004-08-25",
            "entities": ["Nicolás Massú", "Olympic Tennis Centre", "Athens 2004", "Tennis"],
        },
        {
            "doc_id": "DOC_OLY_2008_FENCING",
            "source": "Beijing 2008 Official Games Record",
            "title": "Beijing 2008 Fencing Overview",
            "content": (
                "Fencing at the 2008 Summer Olympics featured 10 distinct events. "
                "The Men's épée competition had 41 competitors competing in the individual tournament held at the Olympic Green Convention Centre. "
                "Matteo Tagliariol of Italy won the gold medal, defeating Fabrice Jeannet of France in the final."
            ),
            "timestamp": "2008-08-18",
            "entities": ["Matteo Tagliariol", "Fencing at the 2008 Summer Olympics – Men's épée", "Beijing 2008"],
        },
        {
            "doc_id": "DOC_OLY_2008_CHINA",
            "source": "Olympic Medal Table Beijing 2008",
            "title": "China Medal Table Summary 2008",
            "content": (
                "Host nation China achieved a total of 100 medals at the 2008 Beijing Summer Olympic Games, "
                "consisting of 51 gold medals, 21 silver medals, and 28 bronze medals, topping the gold medal standings."
            ),
            "timestamp": "2008-08-24",
            "entities": ["China", "Beijing 2008"],
        },
        {
            "doc_id": "DOC_OLY_2004_SWIMMING",
            "source": "Athens 2004 Aquatic Results",
            "title": "Men's 100 Metre Breaststroke Results",
            "content": (
                "At the 2004 Athens Summer Olympics, Kosuke Kitajima of Japan won the gold medal in the Men's 100 metre breaststroke "
                "on 15 August 2004 with a time of 1:00.08. The event had 60 competitors."
            ),
            "timestamp": "2004-08-16",
            "entities": ["Kosuke Kitajima", "Swimming", "Athens 2004"],
        },
    ]

    vstore.add_documents(documents)
    logger.info(f"Ingested {len(documents)} corpus documents and {len(tg.vertices)} graph entity types into engine.")


# Auto-ingest sample corpus on startup
ingest_sample_corpus()
