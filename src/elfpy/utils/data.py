"""
Helper functions for post-processing simulation outputs
"""

import pandas as pd


def format_trades(analysis_dict):
    """Converts the simulator output dictionary to a pandas dataframe and computes derived variables"""
    # construct simulation dataframe output
    trades = pd.DataFrame.from_dict(analysis_dict)
    # calculate derived variables across runs
    trades["pool_apy_percent"] = trades.pool_apy * 100
    trades["vault_apy_percent"] = trades.vault_apy * 100
    trades["time_diff"] = trades.time_until_end.diff()
    trades["time_diff_shift"] = trades.time_until_end.shift(-1).diff()
    trades.loc[len(trades) - 1, "time_diff_shift"] = 1
    trades["fee_in_usd"] = trades.fee
    trades["fee_in_bps"] = trades.fee / trades.out_without_fee * 100 * 100
    base_asset_liquidity_usd = trades.base_asset_reserves * trades.base_asset_price
    token_asset_liquidity_usd = trades.token_asset_reserves * trades.base_asset_price * trades.spot_price
    trades["total_liquidity_usd"] = base_asset_liquidity_usd + token_asset_liquidity_usd
    trades["trade_volume_usd"] = trades.out_with_fee
    # calculate percent change in spot price since the first spot price (after first trade, kinda weird)
    trades["price_total_return"] = (
        trades.loc[:, "spot_price"] / trades.loc[0, "spot_price"] - 1
    )  # rescales price_total_return to equal init_share_price for the first value, for comparison
    trades["price_total_return_scaled_to_share_price"] = (
        trades.price_total_return + 1
    ) * trades.init_share_price  # this is APR (does not include compounding)
    trades["lp_return"] = trades.fee / trades.total_liquidity_usd
    trades["lp_total_return"] = 0
    trades["share_price_total_return"] = 0
    for run in trades.run_number.unique():
        trades.loc[trades.run_number == run, "lp_total_return"] = trades.loc[
            trades.run_number == run, "lp_return"
        ].cumsum()
        trades.loc[trades.run_number == run, "lp_total_return_scaled_to_share_price"] = (
            trades.lp_total_return + 1
        ) * trades.init_share_price  # this is APR (does not include compounding)
        trades.loc[trades.run_number == run, "share_price_total_return"] = (
            trades.loc[trades.run_number == run, "share_price"]
            / trades.loc[trades.run_number == run, "share_price"].iloc[0]
            - 1
        )
    trades["lp_total_return_percent"] = trades.lp_total_return * 100
    trades["price_total_return_percent"] = trades.price_total_return * 100
    trades["share_price_total_return_percent"] = trades.share_price_total_return * 100

    # create explicit column that increments per trade
    trades = trades.reset_index()

    ### STATS AGGREGATED BY DAY ###
    keep_columns = [
        "model_name" if trades.model_name.nunique() > trades.scenario_name.nunique() else "scenario_name",
        "day",
    ]
    trades_agg = trades.groupby(keep_columns).agg(
        {
            "spot_price": ["mean"],
            "trade_volume_usd": ["sum"],
            "fee_in_usd": ["mean", "std", "min", "max", "sum"],
            "fee_in_bps": ["mean", "sum"],
        }
    )
    trades_agg.columns = ["_".join(col).strip() for col in trades_agg.columns.values]
    trades_agg["fee_in_usd_cum_sum"] = 0
    trades_agg = trades_agg.reset_index()
    for model in trades_agg.loc[:,keep_columns[0]].unique():
        trades_agg.loc[trades_agg.loc[:,keep_columns[0]] == model, "fee_in_usd_cum_sum"] = trades_agg.loc[
            trades_agg.loc[:,keep_columns[0]] == model, "fee_in_usd_sum"
        ].cumsum()
    return [trades, trades_agg]
