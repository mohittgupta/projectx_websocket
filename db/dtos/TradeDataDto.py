import datetime
import json
from dataclasses import dataclass, asdict

from config import logger


@dataclass
class TradeDataDTO:
    row_id : int = 0
    comment:str = ""
    user_id : str = ""
    symbol : str = ""
    buy_sell : str = ""
    local_symbol : str = ""
    trade_time : str = ""
    user_price : float = 0
    manual_tp : float = 0
    manual_sl : float = 0
    gtd_in_second : int = 0
    dollar_tp : float = 0
    dollar_sl : float = 0
    stp_limit_stp_price : float = 0
    percentage_tp : float = 0
    percentage_sl : float = 0
    trail_stop : float = 0
    trail_trigger : float = 0
    trail_freq : float = 0
    manual_trail : float = 0
    strategy_name : str = ""
    order_type : str = ""
    quantity : int = 0
    limit_offset : float = 0
    min_tick : float = 0
    stop_offset : float = 0
    TimeInForce : str = ""
    account : str = ""
    processed : bool = False
    status : str = ""
    trade_type : str = ""
    order_id : str = ""
    inst_type : str = ""
    exitTime : str = ""
    oca_group : str = ""
    oca_type : str = ""
    timezone : str = ""
    lmt_price : str = ""
    stp_price : str = ""
    type : str = ""
    Currency : str = ""
    reverse_trade : bool = False
    Exchange : str = ""
    MaturityDate : str = ""
    fromDatetime : str = ""
    toDatetime : str = ""
    moc_order : bool = False
    position_trade : bool = False
    EntryOffsetInPercentage : bool = False
    trailing_stop : bool = False
    trailing_stop_percentage : int = 0
    stop_loss_percentage : bool = False
    take_profit_percentage : bool = False
    eEntryOffset : float = 0
    duplicate_position : bool = False
    rth : bool = False
    maximumOrder : int = 0
    sttpexitTime : int = 0
    tradeDate : datetime = None
    demo : bool = False
    entry_id : str = ""
    lmt_id : str = ""
    stp_id : str = ""
    close_ids : str = ""
    update_ids : str = ""
    alert_data : str = ""
    entry_order_type : str = ""
    lmt_order_type : str = ""
    stp_order_type : str = ""
    entry_order_status : str = ""
    lmt_order_status : str = ""
    stp_order_status : str = ""
    alert_status : str = ""
    random_key : str = ""
    platform : str = ""
    server_date_time : datetime = None


    def __str__(self):
            return json.dumps(asdict(self))

