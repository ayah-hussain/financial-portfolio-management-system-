import psycopg2
from datetime import datetime, timedelta
import random
from psycopg2.extras import execute_values
import numpy as np
import pandas as pd
import os
from psycopg2.extras import execute_values
import bcrypt  # Secure password hashing


# Database connection parameters
DB_PARAMS = {
    "dbname": "portfoliovantage",
    "user": os.getenv("USER", "string"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": "localhost",
    "port": "5432"
}

# Sample data
STOCK_DATA = [
    ("AAPL", "Apple Inc.", "stock", "Yahoo Finance"),
    ("MSFT", "Microsoft Corporation", "stock", "Yahoo Finance"),
    ("GOOGL", "Alphabet Inc.", "stock", "Yahoo Finance"),
    ("AMZN", "Amazon.com Inc.", "stock", "Yahoo Finance"),
    ("META", "Meta Platforms Inc.", "stock", "Yahoo Finance"),
    ("TSLA", "Tesla Inc.", "stock", "Yahoo Finance"),
    ("NVDA", "NVIDIA Corporation", "stock", "Yahoo Finance"),
    ("JPM", "JPMorgan Chase & Co.", "stock", "Yahoo Finance"),
    ("V", "Visa Inc.", "stock", "Yahoo Finance"),
    ("JNJ", "Johnson & Johnson", "stock", "Yahoo Finance")
]

NEWS_CATEGORIES = ["Market Analysis", "Company News", "Industry Trends", "Economic Updates", "Technology"]
NEWS_SOURCES = ["Bloomberg", "Reuters", "CNBC", "Financial Times", "Wall Street Journal"]
SENTIMENTS = ["Ultra-Bullish", "Positive", "Neutral", "Negative", "Ultra-Bearish"]

def connect_db():
    return psycopg2.connect(**DB_PARAMS)

#Hashes a password using bcrypt for security.
def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

#Creates dummy users with hashed passwords and stores them in the database.
def create_users(conn, num_users=5):
    with conn.cursor() as cur:
        users_data = []
        user_ids = []
        for i in range(num_users):
            username = f"user{i+1}"
            cur.execute("""
                INSERT INTO users (username, password, email)
                VALUES (%s, %s, %s)
                ON CONFLICT (username) DO NOTHING
                RETURNING userid;
            """, (username, hash_password(f"password{i+1}"), f"{username}@example.com"))
            result = cur.fetchone()
            if result:
                user_ids.append(result[0])
            else:
                # If user already exists, get their ID
                cur.execute("SELECT userid FROM users WHERE username = %s", (username,))
                user_ids.append(cur.fetchone()[0])
        return user_ids

def generate_gbm(start_price, mu, sigma, T, dt):
    """
    Generate stock prices using Geometric Brownian Motion.

    Parameters:
    - start_price: Initial stock price
    - mu: Expected return
    - sigma: Volatility
    - T: Total time (in days)
    - dt: Time step (in days)

    Returns:
    - pandas DataFrame with simulated stock prices
    """
    N = int(T / dt)  # Number of time steps
    t = np.linspace(0, T, N)
    W = np.random.standard_normal(size=N) 
    W = np.cumsum(W) * np.sqrt(dt)  # Brownian motion
    X = (mu - 0.5 * sigma**2) * t + sigma * W
    S = start_price * np.exp(X)  # GBM formula
    return S

def create_assets(conn):
    """
    Inserts predefined stock assets into the database.
    If an asset already exists (based on ticker), it is ignored.

    """
    with conn.cursor() as cur:
        asset_ids = []
        # Insert assets into the database
        for ticker, name, asset_type, source in STOCK_DATA:
            # Bulk Insert using execute_values for efficiency
            cur.execute("""
                INSERT INTO assets (ticker, assetname, assettype, source)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (ticker) DO UPDATE 
                SET assetname = EXCLUDED.assetname
                RETURNING assetid
            """, (ticker, name, asset_type, source))
            # Store asset IDs
            asset_ids.append(cur.fetchone()[0])
        return asset_ids



def create_price_history(conn, asset_ids):
    """
    Generates and inserts realistic price history for assets using Geometric Brownian Motion (GBM).
    Simulates 5 years of daily prices for each asset and stores them in the database.
    """

    with conn.cursor() as cursor:
        # Generate 1 year of daily prices
        days = 365 * 5
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        price_data = []
        for asset_id in asset_ids:
            # Start with a realistic base price between $10 and $1000
            base_price = random.uniform(10, 1000)
            
            # Generate daily prices with more realistic parameters
            # mu = 0.0002 (5% annual return)
            # sigma = 0.01 (16% annual volatility)
            prices = generate_gbm(
                start_price=base_price,
                mu=0.0002,  # Daily drift (5% annual return)
                sigma=0.01,  # Daily volatility (16% annual volatility)
                T=days,
                dt=1.0  # One price per day
            )

            current_date = start_date
            for price in prices:
                # Ensure price is positive and has reasonable decimals
                price = float(max(0.01, round(price, 2)))
                price_data.append((
                    asset_id,
                    current_date,
                    price
                ))
                current_date += timedelta(days=1)
        
        # Batch insert the price data
        execute_values(cursor, """
            INSERT INTO pricehistory (assetid, timestamp, price)
            VALUES %s
            ON CONFLICT (assetid, timestamp) DO UPDATE 
            SET price = EXCLUDED.price
        """, price_data)

        conn.commit() # Ensure data is committed


#Creates 1 to 3 portfolios per user and inserts them into the database efficiently.
def create_portfolios(conn, user_ids):   
    
    with conn.cursor() as cur:
        portfolio_data = []  

        # Collect portfolio data for all users
        for user_id in user_ids:
            num_portfolios = random.randint(1, 3)
            portfolio_data.extend([(user_id, f"Portfolio {i+1}") for i in range(num_portfolios)])

        if portfolio_data:  
            # Bulk insert all portfolios at once
            execute_values(cur, """
                INSERT INTO portfolios (userid, portfolioname) 
                VALUES %s 
                RETURNING portfolioid
            """, portfolio_data)

            # Store portfolio IDs 
            portfolio_ids = [row[0] for row in cur.fetchall()]
            conn.commit()  # Ensure data is saved

        return portfolio_ids
         

#Assigns 3-7 random assets to each portfolio and stores them in the database efficiently.
def create_portfolio_assets(conn, portfolio_ids, asset_ids):
    with conn.cursor() as cur:
        for portfolio_id in portfolio_ids:
            # Add 3-7 random assets to each portfolio
            selected_assets = random.sample(asset_ids, random.randint(3, 7))

            for asset_id in selected_assets:
                cur.execute("SELECT ticker FROM assets WHERE assetid = %s", (asset_id,))
                ticker = cur.fetchone()[0]
                
                quantity = random.randint(1, 100)
                price = random.uniform(50, 500)
                
                cur.execute("""
                    INSERT INTO portfolioassets (portfolioid, assetid, ticker, quantity, averagepurchaseprice)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (portfolioid, assetid) DO UPDATE 
                    SET quantity = EXCLUDED.quantity,
                        averagepurchaseprice = EXCLUDED.averagepurchaseprice
                """, (portfolio_id, asset_id, ticker, quantity, price))
    conn.commit()  # Ensure data is saved

#Generate news using helper data 
def create_news(conn, asset_ids):
    with conn.cursor() as cur:
        news_ids = []
        
        # Templates for more realistic news titles and content
        TITLE_TEMPLATES = [
            "{company} Reports {direction} Q{quarter} Earnings, {outcome}",
            "Breaking: {company} Announces {announcement_type}",
            "{company} Stock {movement} After {event}",
            "Market Analysis: {company}'s {sector} Position Strengthens",
            "Investors React to {company}'s Latest {news_type}"
        ]
        
        CONTENT_TEMPLATES = [
            """
            {company} ({ticker}) today announced its {timeframe} financial results, reporting {metric} of ${amount} billion, 
            {comparison} analysts' expectations. The company's {segment} segment showed particularly {performance}, 
            with revenue {direction} by {percentage}% year-over-year.

            CEO {executive} commented, "Our {timeframe} results demonstrate the strength of our {strategy} strategy 
            and our continued focus on {focus_area}." The company also {additional_action}, which analysts view as {analyst_view}.

            Looking ahead, {company} expects to {future_plan} in the coming quarters, with a focus on {focus_area}. 
            The company's guidance for the next quarter suggests {outlook} growth, with projected revenue between 
            ${revenue_low} billion and ${revenue_high} billion.
            """,
            
            """
            In a significant development for the {sector} sector, {company} ({ticker}) has {announcement}. 
            This move comes as the company seeks to {strategic_goal} in an increasingly competitive market.

            Industry analysts at {firm} note that this {action_type} could {impact} the company's market position. 
            "{analysis_quote}", said {analyst_name}, senior analyst at {firm}.

            The announcement has led to {market_reaction} among investors, with the stock {stock_movement} in 
            {trading_session} trading. The company's {metric} currently stands at ${amount} billion, reflecting 
            a {percentage}% {direction} from previous {timeframe}.
            """,
            
            """
            Market watchers are closely monitoring {company} ({ticker}) as it {recent_action}. The {sector} giant 
            has been {trend} in recent months, leading to {consequence} in its core markets.

            The company's recent {initiative} has garnered attention from {stakeholder}, who {stakeholder_action}. 
            This development comes amid {market_condition} in the broader {sector} sector.

            {company}'s {department} team has {action}, which is expected to {impact} the company's {metric} by 
            approximately {percentage}% over the next {timeframe}. The move has been {reception} by industry experts.
            """
        ]
        
        # Helper data for generating content
        EXECUTIVES = ["John Smith", "Sarah Johnson", "Michael Chen", "Emily Brown", "David Wilson"]
        FIRMS = ["Goldman Sachs", "Morgan Stanley", "JP Morgan", "Citi Research", "Bank of America"]
        ANALYSTS = ["Robert Williams", "Jennifer Lee", "Mark Thompson", "Lisa Chen", "James Anderson"]
        METRICS = ["revenue", "net income", "operating margin", "market share", "user growth"]
        STRATEGIES = ["digital transformation", "market expansion", "innovation", "cost optimization", "sustainable growth"]
        
        # Create 50 news articles
        for _ in range(50):
            # Select a random asset for this news
            asset_id = random.choice(asset_ids)
            cur.execute("SELECT ticker, assetname FROM assets WHERE assetid = %s", (asset_id,))
            ticker, company = cur.fetchone()
            
            # Generate random data for templates
            data = {
                "company": company,
                "ticker": ticker,
                "timeframe": random.choice(["Q1", "Q2", "Q3", "Q4", "annual"]),
                "metric": random.choice(METRICS),
                "amount": round(random.uniform(1, 100), 2),
                "comparison": random.choice(["exceeding", "meeting", "falling short of"]),
                "segment": random.choice(["cloud", "consumer", "enterprise", "mobile", "services"]),
                "performance": random.choice(["strong", "mixed", "challenging"]),
                "direction": random.choice(["increased", "decreased", "grew", "declined"]),
                "percentage": round(random.uniform(5, 30), 1),
                "executive": random.choice(EXECUTIVES),
                "strategy": random.choice(STRATEGIES),
                "focus_area": random.choice(["innovation", "market expansion", "customer experience", "operational efficiency"]),
                "additional_action": random.choice([
                    "announced a stock buyback program",
                    "revealed plans for international expansion",
                    "introduced new product lines",
                    "restructured its leadership team"
                ]),
                "analyst_view": random.choice(["positive", "cautiously optimistic", "neutral", "concerning"]),
                "future_plan": random.choice([
                    "expand its market presence",
                    "launch new products",
                    "optimize operations",
                    "invest in R&D"
                ]),
                "revenue_low": round(random.uniform(10, 50), 2),
                "revenue_high": round(random.uniform(51, 100), 2),
                "sector": random.choice(["technology", "finance", "healthcare", "retail", "energy"]),
                "announcement": random.choice([
                    "announced a major acquisition",
                    "launched a groundbreaking product",
                    "entered a strategic partnership",
                    "initiated a corporate restructuring"
                ]),
                "firm": random.choice(FIRMS),
                "analyst_name": random.choice(ANALYSTS),
                "trading_session": random.choice(["morning", "afternoon", "after-hours"]),
                "stock_movement": random.choice(["rising sharply", "trading higher", "declining", "remaining stable"]),
                "news_type": random.choice(["earnings report", "product launch", "partnership announcement", "market analysis"]),
                "movement": random.choice(["surges", "plummets", "rises", "falls"]),
                "quarter": random.choice(["Q1", "Q2", "Q3", "Q4"]),
                "announcement_type": random.choice(["major acquisition", "product launch", "strategic partnership"]),
                "recent_action": random.choice(["announced earnings", "launched a new product", "acquired a competitor"]),
                "trend": random.choice(["struggling", "thriving", "growing", "contracting"]),
                "outlook": random.choice(["moderate", "strong", "weak"]),
                "consequence": random.choice(["significant changes", "limited impact", "market disruption"]),
                "event": random.choice(["earnings report", "product launch", "partnership announcement"]),
                "strategic_goal": random.choice(["expand market share", "drive innovation", "improve profitability"]),
                "outcome": random.choice(["beating", "missing", "meeting"]),
                "initiative": random.choice(["cost-cutting", "expansion", "restructuring"]),
                "action_type": random.choice(["strategic move", "market entry", "product launch"]),
                "stakeholder": random.choice(["investors", "analysts", "industry experts"]),
                "impact": random.choice(["influence", "affect", "impact"]),
                "stakeholder_action": random.choice(["expressed optimism", "raised concerns", "remained neutral"]),
                "analysis_quote": random.choice([ "This move is a game-changer", "The impact remains to be seen", "A bold strategic decision"]),
                "market_condition": random.choice(["rapid changes", "stagnation", "intense competition"]),
                "market_reaction": random.choice(["mixed reactions", "enthusiasm", "concerns"]),
                "department": random.choice(["R&D", "marketing", "sales", "operations"]),
                "action": random.choice(["launched a new initiative", "restructured its operations", "expanded into new markets"]),
                "reception": random.choice(["well-received", "met with skepticism", "greeted positively"]),
            }
            
            # Generate title and content using templates
            title = random.choice(TITLE_TEMPLATES).format(**data)
            content = random.choice(CONTENT_TEMPLATES).format(**data)
            
            published_date = datetime.now() - timedelta(days=random.randint(0, 30))
            
            cur.execute("""
                INSERT INTO news (category, title, content, source, author, publishedat)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING newsid
            """, (
                random.choice(NEWS_CATEGORIES),
                title,
                content.strip(),
                random.choice(NEWS_SOURCES),
                f"{random.choice(ANALYSTS)}, {random.choice(FIRMS)}",
                published_date
            ))
            news_ids.append(cur.fetchone()[0])
        return news_ids

#Associates news articles with 1-3 random assets and stores them efficiently in the database.
def create_news_asset_tags(conn, news_ids, asset_ids):
    with conn.cursor() as cur:
        for news_id in news_ids:
            # Tag 1-3 random assets for each news article
            selected_assets = random.sample(asset_ids, random.randint(1, 3))

            for asset_id in selected_assets:
                cur.execute("SELECT ticker FROM assets WHERE assetid = %s", (asset_id,))
                ticker = cur.fetchone()[0]
                
                cur.execute("""
                    INSERT INTO newsassettags (newsid, assetid, ticker)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (newsid, assetid) DO NOTHING
                """, (news_id, asset_id, ticker))
    conn.commit()


#Creates user interactions with news articles
def create_news_interactions(conn, news_ids, user_ids):
    with conn.cursor() as cur:
        for news_id in news_ids:
            # Create interactions for 1-3 random users per news article
            selected_users = random.sample(user_ids, random.randint(1, 3))
            for user_id in selected_users:
                cur.execute("""
                    INSERT INTO newsinteractions (newsid, userid, sentiment, comment)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (newsid, userid) DO NOTHING
                """, (
                    news_id,
                    user_id,
                    random.choice(SENTIMENTS),
                    f"Sample comment from user {user_id} about news {news_id}"
                ))
    conn.commit()   

def main():
    conn = connect_db()
    try:
        print("Creating users...")
        user_ids = create_users(conn)
        
        print("Creating assets...")
        asset_ids = create_assets(conn)
        
        print("Creating price history...")
        create_price_history(conn, asset_ids)
        
        print("Creating portfolios...")
        portfolio_ids = create_portfolios(conn, user_ids)
        
        print("Creating portfolio assets...")
        create_portfolio_assets(conn, portfolio_ids, asset_ids)
        
        print("Creating news articles...")
        news_ids = create_news(conn, asset_ids)
        
        print("Creating news asset tags...")
        create_news_asset_tags(conn, news_ids, asset_ids)
        
        print("Creating news interactions...")
        create_news_interactions(conn, news_ids, user_ids)
        
        conn.commit()
        print("Successfully populated database with dummy data!")
         
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main() 