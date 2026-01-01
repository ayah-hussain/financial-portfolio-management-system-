-- Drop existing tables in reverse order of dependencies
DROP TABLE IF EXISTS newsinteractions CASCADE;
DROP TABLE IF EXISTS newsassettags CASCADE;
DROP TABLE IF EXISTS news CASCADE;
DROP TABLE IF EXISTS pricehistory CASCADE;
DROP TABLE IF EXISTS portfoliosnapshots CASCADE;
DROP TABLE IF EXISTS portfolioassets CASCADE;
DROP TABLE IF EXISTS assets CASCADE;
DROP TABLE IF EXISTS portfolios CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Users Table
CREATE TABLE users (
    userid SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    createdat TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Portfolios Table
CREATE TABLE portfolios (
    portfolioid SERIAL PRIMARY KEY,
    userid INTEGER NOT NULL REFERENCES users(userid) ON DELETE CASCADE,
    portfolioname VARCHAR(100) NOT NULL,
    createdat TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Assets Table
CREATE TABLE assets (
    assetid SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL UNIQUE,
    assetname VARCHAR(100) NOT NULL,
    assettype VARCHAR(50) NOT NULL,
    source VARCHAR(100) NOT NULL,
    lastupdated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Portfolio Assets Table
CREATE TABLE portfolioassets (
    portfolioid INTEGER REFERENCES portfolios(portfolioid) ON DELETE CASCADE,
    assetid INTEGER REFERENCES assets(assetid) ON DELETE CASCADE,
    ticker VARCHAR(20) NOT NULL REFERENCES assets(ticker),
    quantity DECIMAL(15,2) NOT NULL DEFAULT 0,
    averagepurchaseprice DECIMAL(15,2) NOT NULL,
    PRIMARY KEY (portfolioid, assetid)
);

-- Portfolio Snapshots Table
CREATE TABLE portfoliosnapshots (
    portfolioid INTEGER REFERENCES portfolios(portfolioid) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,
    totalvalue DECIMAL(15,2) NOT NULL,
    PRIMARY KEY (portfolioid, timestamp)
);

-- Price History Table
CREATE TABLE pricehistory (
    assetid INTEGER REFERENCES assets(assetid) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,
    price DECIMAL(15,2) NOT NULL,
    PRIMARY KEY (assetid, timestamp)
);

-- News Table
CREATE TABLE news (
    newsid SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(100) NOT NULL,
    author VARCHAR(100) NOT NULL,
    publishedat TIMESTAMP NOT NULL,
    createdat TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- News Asset Tags Table
CREATE TABLE newsassettags (
    newsid INTEGER REFERENCES news(newsid) ON DELETE CASCADE,
    assetid INTEGER REFERENCES assets(assetid) ON DELETE CASCADE,
    ticker VARCHAR(20) NOT NULL REFERENCES assets(ticker),
    createdat TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (newsid, assetid)
);

-- News Interactions Table
CREATE TABLE newsinteractions (
    newsid INTEGER REFERENCES news(newsid) ON DELETE CASCADE,
    userid INTEGER REFERENCES users(userid) ON DELETE CASCADE,
    sentiment VARCHAR(20) NOT NULL CHECK (sentiment IN ('Ultra-Bullish', 'Positive', 'Neutral', 'Negative', 'Ultra-Bearish')),
    comment TEXT,
    createdat TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (newsid, userid)
);

-- Create indexes for better query performance
CREATE INDEX idx_portfolios_userid ON portfolios(userid);
CREATE INDEX idx_portfolioassets_assetid ON portfolioassets(assetid);
CREATE INDEX idx_pricehistory_timestamp ON pricehistory(timestamp);
CREATE INDEX idx_news_publishedat ON news(publishedat);
CREATE INDEX idx_newsassettags_assetid ON newsassettags(assetid);
CREATE INDEX idx_newsinteractions_userid ON newsinteractions(userid); 