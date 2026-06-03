from ingestion.ingest_company import ingest_company

with open("./data/watchlist.txt", "r") as f:
    watchlist = [line.strip() for line in f if line.strip()]

if __name__ == "__main__":
    for cik in watchlist:
        ingest_company(cik)