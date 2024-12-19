import dlt
from debank_pipeline import *
from dune_pipeline import *

def loop_through_cover_wallets():
  wallet = "0xbad"

  try:
    # fetch cover wallets as df
    pipeline = dlt.pipeline(
      pipeline_name="fetch_cover_wallets",
      destination="motherduck",
      dataset_name="main"
    )

    with pipeline.sql_client() as client:
      with client.execute_query("SELECT DISTINCT cover_id, monitored_wallet FROM cover_wallets") as cursor:
        result_df = cursor.df()
    
    if not result_df.empty:
      for _, row in result_df.iterrows():
        cover_id = row["cover_id"]
        wallet = row["monitored_wallet"]
        load_user_all_simple_protocol_list(cover_id, wallet)

  except Exception as e:
    print(f"error for cover_id: {cover_id} and wallet: {wallet}: {e}")

if __name__ == "__main__":
  # get last loaded cover_id and append all new ones
  pipeline = dlt.pipeline(
    pipeline_name="read_max_cover_id",
    destination="motherduck",
    dataset_name="main"
  )

  with pipeline.sql_client() as client:
    with client.execute_query("SELECT MAX(cover_id) FROM cover_wallets") as cursor:
      max_cover_id = cursor.fetchone()[0]

  if max_cover_id > 0:
    load_cover_wallets(max_cover_id)
  
  # flush & fill load
  load_capital_pool()

  # append current wallet balances
  loop_through_cover_wallets()
