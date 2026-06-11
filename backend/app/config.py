import os
from pathlib import Path

# Paths
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
WORKSPACE_ROOT = BACKEND_DIR.parent

MODEL_PATH = WORKSPACE_ROOT / "model.pkl"
LABEL_ENCODER_PATH = WORKSPACE_ROOT / "label_encoder.pkl"
FACT_EMBEDDINGS_PATH = WORKSPACE_ROOT / "fact_embeddings.pkl"
TRUSTED_FACTS_PATH = WORKSPACE_ROOT / "trusted_facts.pkl"
CSV_DATA_PATH = WORKSPACE_ROOT / "fake_or_real_news.csv"

STATIC_DIR = BACKEND_DIR / "static"

# Model Configurations
MODEL_NAME = "all-mpnet-base-v2"
DEFAULT_SAMPLES = 1000  # Default number of samples to train on if fallback training is triggered

# Default trusted facts list if trusted_facts.pkl is missing
DEFAULT_TRUSTED_FACTS = [
    # --- US Elections & Politics ---
    "donald trump won the 2016 presidential election with 306 electoral college votes",
    "hillary clinton won the popular vote in the 2016 presidential election by nearly three million votes",
    "the fbi investigated hillary clinton use of private email server while secretary of state",
    "fbi director james comey announced no criminal charges recommended against hillary clinton",
    "barack obama served two terms as president of the united states from 2009 to 2017",
    "the us electoral college consists of 538 electors and a majority of 270 is needed to win",
    "congress certified the 2020 presidential election results confirming joe biden victory",
    "the january 6 2021 capitol building breach interrupted the certification of electoral votes",
    "the senate intelligence committee investigated russian interference in the 2016 election",
    "robert mueller special counsel investigation examined russian interference in us elections",
    "the mueller report did not establish that the trump campaign conspired with russia",
    "us midterm elections are held every two years to elect members of congress",
    "the affordable care act also known as obamacare was signed into law in 2010",
    "supreme court justice ruth bader ginsburg died in september 2020",
    "amy coney barrett was confirmed to the supreme court in october 2020",
    "the us senate acquitted donald trump in both impeachment trials",
    "joe biden won the 2020 presidential election defeating incumbent donald trump",

    # --- Vaccines & Public Health ---
    "health officials and scientific studies confirm vaccines do not cause autism",
    "the wakefield study claiming vaccines cause autism was retracted and found fraudulent",
    "andrew wakefield lost his medical license after his discredited autism vaccine study",
    "the mmr vaccine protects against measles mumps and rubella and is considered safe",
    "the covid 19 mrna vaccines do not alter human dna according to medical experts",
    "mrna vaccines teach cells to produce a protein that triggers an immune response",
    "the world health organization declared covid 19 a global pandemic in march 2020",
    "the us food and drug administration fda authorized covid 19 vaccines for emergency use",
    "herd immunity occurs when enough of a population becomes immune to a disease",
    "vaccine ingredients are publicly listed and do not include microchips or tracking devices",
    "the cdc recommends flu vaccines annually as the influenza virus mutates each year",
    "clinical trials test vaccines for safety and efficacy before regulatory approval",
    "polio was nearly eradicated worldwide due to widespread vaccination programs",
    "natural immunity and vaccine induced immunity both help prevent infectious disease spread",
    "covid 19 vaccines were developed using spike protein technology to stimulate immunity",

    # --- Science & Space ---
    "nasa monitors near earth objects and has found no imminent asteroid threat to earth",
    "the planetary defense coordination office tracks potentially hazardous asteroids and comets",
    "climate change is driven primarily by human greenhouse gas emissions according to nasa and noaa",
    "the intergovernmental panel on climate change ipcc reports scientific consensus on global warming",
    "carbon dioxide levels in the atmosphere have risen significantly since the industrial revolution",
    "the paris agreement is an international treaty on climate change adopted in 2015",
    "nasa confirmed water ice exists on the moon in permanently shadowed craters",
    "the james webb space telescope launched in december 2021 and began science operations in 2022",
    "black holes are regions of spacetime where gravity is so strong nothing can escape",
    "the big bang theory describes the origin of the universe approximately 13 8 billion years ago",
    "spacex successfully launched and landed reusable orbital rockets reducing launch costs",
    "the international space station has been continuously inhabited since november 2000",

    # --- Economics & Finance ---
    "the us federal reserve sets interest rates to manage inflation and economic growth",
    "the 2008 financial crisis was triggered by the collapse of the subprime mortgage market",
    "the dodd frank act was passed in 2010 to regulate financial institutions after the 2008 crisis",
    "us gdp is measured quarterly and represents the total economic output of the country",
    "the unemployment rate measures the percentage of the labor force actively seeking work",
    "tariffs are taxes imposed on imported goods and can raise prices for consumers",
    "the stock market experienced significant volatility during the covid 19 pandemic in 2020",
    "bitcoin is a decentralized digital currency not backed by any government or central bank",

    # --- Law Enforcement & Legal ---
    "the department of justice oversees federal law enforcement agencies including the fbi",
    "the fourth amendment protects americans from unreasonable searches and seizures",
    "the first amendment protects freedom of speech press religion and assembly",
    "the second amendment protects the right to keep and bear arms",
    "the supreme court ruled in citizens united that political spending is protected speech",
    "plea bargains resolve the majority of criminal cases in the us court system",
    "the patriot act expanded surveillance powers of us intelligence agencies after september 11",
    "edward snowden leaked classified nsa documents revealing mass surveillance programs in 2013",

    # --- Media & Misinformation ---
    "facebook and twitter implemented fact checking labels on posts containing misinformation",
    "the term fake news refers to deliberate disinformation presented as legitimate journalism",
    "media literacy education helps people identify credible sources and recognize bias",
    "social media algorithms can amplify misinformation due to high engagement on emotional content",
    "the associated press reuters and bbc are considered internationally recognized news sources",
    "satirical news websites like the onion publish fictional stories not intended as real news",
    "the fairness doctrine required broadcast media to present contrasting views on controversial issues",
    "deepfake technology uses artificial intelligence to create realistic fake videos of real people",

    # --- Immigration ---
    "daca deferred action for childhood arrivals protects undocumented immigrants brought as children",
    "the us border patrol is responsible for securing us borders between ports of entry",
    "immigration courts are part of the department of justice not the federal judiciary",
    "asylum seekers must demonstrate fear of persecution in their home country to qualify",
    "the immigration and nationality act establishes the legal framework for us immigration policy",

    # --- Terrorism & National Security ---
    "the september 11 2001 attacks were carried out by al qaeda killing nearly 3000 people",
    "the us invaded afghanistan in 2001 following the september 11 attacks",
    "osama bin laden was killed by us navy seals in pakistan in may 2011",
    "isis also known as isil or daesh is a jihadist militant group that emerged in iraq and syria",
    "the department of homeland security was created after september 11 to coordinate domestic security",
    "the patriot act gave law enforcement broader surveillance authority following the 9 11 attacks",

    # NASA Artemis
    "nasa artemis program aims to return humans to the moon including the first woman",
    "the space launch system sls is nasa primary rocket for deep space exploration",
    "the orion capsule is designed to carry astronauts to the moon and deep space",
    "nasa is working with esa jaxa and csa on the lunar gateway space station",
    "nasa completed an uncrewed artemis test flight gathering critical engineering data",
    "the lunar gateway is a planned space station orbiting the moon for future missions",
    "nasa plans to establish a sustainable human presence on the moon before going to mars",
    "spacex boeing and other private companies are partners in nasa commercial crew program"
]
