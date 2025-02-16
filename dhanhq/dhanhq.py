#class to use dhan api

import logging
import requests
from json import loads as json_loads, dumps as json_dumps


class dhanhq:
    
    #declaring constants
    NSE= 'NSE_EQ'
    BSE= 'BSE_EQ'
    CUR= 'NSE_CURRENCY'
    MCX= 'MCX_COMM'
    FNO= 'NSE_FNO'
    BUY= B= 'BUY'
    SELL= S= 'SELL'
    CNC= 'CNC'
    INTRA= "INTRADAY"
    SL= "STOP_LOSS"
    SLM= "STOP_LOSS_MARKET"
    MARGIN= 'MARGIN'
    CO= 'CO'
    BO= 'BO'
    LIMIT= 'LIMIT'
    MARKET= 'MARKET'
    DAY= 'DAY'
    IOC= 'IOC'
    GTC= 'GTC'
    GTD= 'GTD'
    def __init__(self,client_id,access_token):
        try:
            self.client_id= str(client_id)
            self.access_token= access_token
            self.base_url= 'https://api.dhan.co'
            self.timeout= 60 #used for http requests
            self.header= {
                'access-token': access_token,
                'content-type': 'application/json',
            }
            requests.packages.urllib3.util.connection.HAS_IPV6 = False
            self.session= requests.Session()
        except Exception as e:
            logging.error('Exception in dhanhq>>init : %s',e)

    def _parse_response(self,response):
        try:
            status= 'failure'
            remarks=''
            data=''
            python_response= json_loads(response.content)
            if response.status_code==200:
                status= 'success'
                remarks=''
                data= python_response
            else:
                error_code=python_response['internalErrorCode']
                error_logs= python_response['internalErrorMessage']
                remarks= {
                    'error_code':error_code,
                    'message':error_logs
                }
        except Exception as e:
            logging.warning('Exception found in dhanhq>>find_error_code: %s',e)
            status= 'failure'
            remarks= str(e)
        return {
            'status':status,
            'remarks':remarks,
            'data':data,
        }

    def get_order_list(self):
        """Retrieve a list of all orders requested in a day with their last updated status."""
        try:
            url= self.base_url+'/orders'
            response= self.session.get(url,headers=self.header,timeout= self.timeout)
            return self._parse_response(response)
        except Exception as e:
            logging.error('Exception in dhanhq>>get_order_list : %s',e)
            return {
                'status':'failure',
                'remarks':f'Exception in dhanhq>>get_order_list : {e}',
                'data':'',
            }

    def get_order_by_id(self,order_id):
        """Retrieve the details and status of an order from the orderbook placed during the day."""
        try:
            url= self.base_url+f'/orders/{order_id}'
            response= self.session.get(url,headers=self.header,timeout= self.timeout)
            return self._parse_response(response)
        except Exception as e:
            logging.error('Exception in dhanhq>>get_order_by_id : %s',e)
            error= str(e)
            return {
                'status':'failure',
                'remarks':f'Exception in dhanhq>>get_order_by_id : {e}',
                'data':'',
            }

    def modify_order(self,order_id,order_type,leg_name,quantity,price,trigger_price,disclosed_quantity,validity):
        """Modify pending order in orderbook. The variables that can be modified are price, quantity, order type & validity."""
        try:
            url= self.base_url+f'/orders/{order_id}'
            payload={
                    "dhanClientId": self.client_id,
                    "orderId": str(order_id),
                    "orderType": order_type,
                    "legName": leg_name,
                    "quantity": quantity,
                    "price": price,
                    "disclosedQuantity": disclosed_quantity,
                    "triggerPrice": trigger_price,
                    "validity": validity
            }
            payload= json_dumps(payload)
            response= self.session.put(url,headers=self.header,timeout= self.timeout, data=payload)
            return self._parse_response(response)
        except Exception as e:
            logging.error('Exception in dhanhq>>modify_order: %s',e)
            error= str(e)
            return {
                'status':'failure',
                'remarks':str(e),
                'data':'',
            }

    def cancel_order(self,order_id):
        """Cancel a pending order in the orderbook using the order id of an order."""
        try:
            url= self.base_url+f'/orders/{order_id}'
            response= self.session.delete(url,headers=self.header,timeout= self.timeout)
            return self._parse_response(response)
        except Exception as e:
            logging.error('Exception in dhanhq>>cancel_order: %s',e)
            return {
                'status':'failure',
                'remarks':str(e),
                'data':'',
            }

    def place_order(self,security_id,exchange_segment,transaction_type,quantity,\
        order_type,product_type,price,trigger_price=0,disclosed_quantity=0,\
        after_market_order=False,validity='DAY',amo_time='OPEN',tag=None):
        """Place new Orders"""
        #place order in Dhan account
        #security_id(str),exchange_segment(str),transaction_type(str),
        #quantity(int),order_type(str),validity(str),product_type(str),
        #price(float),trigger_price(float),disclosed_quantity(int),
        #after_market_order(Boolean),amo_time(str),tag(str)
        
        try:
            url= self.base_url+'/orders'
            payload={
                    "dhanClientId": self.client_id,
                    "transactionType": transaction_type.upper(),
                    "exchangeSegment": exchange_segment.upper(),
                    "productType": product_type.upper(),
                    "orderType": order_type.upper(),
                    "validity": validity.upper(),
                    "securityId": security_id,
                    "quantity": int(quantity),
                    "disclosedQuantity": int(disclosed_quantity),
                    "price": float(price),
                    "afterMarketOrder": after_market_order,
                }
            if tag!=None and tag!='':
                payload["correlationId"] = tag,
            if after_market_order== True:
                if amo_time in ['OPEN','OPEN_30','OPEN_60']:
                    payload['amoTime'] = amo_time
                else:
                    raise Exception("amo_time value must be ['OPEN','OPEN_30','OPEN_60']")
            if trigger_price>0:
                payload["triggerPrice"]= float(trigger_price)
            elif trigger_price==0:
                payload["triggerPrice"]= 0.0
            payload= json_dumps(payload)
            response= self.session.post(url,data=payload,headers=self.header,timeout=self.timeout)
            return self._parse_response(response)
        except Exception as e:
            logging.error('Exception in dhanhq>>place_order: %s',e)
            return {
                'status':'failure',
                'remarks':str(e),
                'data':'',
            }

    def get_order_by_corelationID(self,corelationID):
        """Retrieves the order status using a field called correlation id, Provided by API consumer during order placement."""
        try:
            url= self.base_url+f'/orders/external/{corelationID}'
            response= self.session.get(url,headers=self.header,timeout=self.timeout)
            return self._parse_response(response)
        except Exception as e:
            logging.error('Exception in dhanhq>>get_order_by_corelationID: %s',e)
            return {
                'status':'failure',
                'remarks':str(e),
                'data':'',
                'error_logs':''
            }

    def get_positions(self):
        """Retrieve a list of all open positions for the day. This includes all F&O carryforward positions as well."""
        try:
            url= self.base_url+f'/positions'
            response= self.session.get(url,headers=self.header,timeout=self.timeout)
            return self._parse_response(response)
        except Exception as e:
            logging.error('Exception in dhanhq>>get_positions: %s',e)
            return {
                'status':'failure',
                'remarks':str(e),
                'data':'',
            }

    def get_holdings(self):
        """Retrieve all holdings bought/sold in previous trading sessions. All T1 and delivered quantities can be fetched."""
        try:
            url= self.base_url+f'/holdings'
            response= self.session.get(url,headers=self.header,timeout=self.timeout)
            return self._parse_response(response)
        except Exception as e:
            logging.error('Exception in dhanhq>>get_holdings: %s',e)
            return {
                'status':'failure',
                'remarks':str(e),
                'data':'',
            }
    
    def intraday_daily_minute_charts(self,security_id,exchange_segment,instrument_type):
        """Retrieve OHLC & Volume of 1 minute candle for desired instrument for current day. This data available for all segments including futures & options."""
        try:
            url= self.base_url+f'/charts/intraday'
            payload= {
                'securityId':security_id,
                'exchangeSegment':exchange_segment,
                'instrument':instrument_type
            }
            payload= json_dumps(payload)
            response= self.session.post(url,headers=self.header,timeout=self.timeout,data=payload)
            return self._parse_response(response)
        except Exception as e:
            logging.error('Exception in dhanhq>>intraday_daily_minute_charts: %s',e)
            return {
                'status':'failure',
                'remarks':str(e),
                'data':'',
            }

    def historical_minute_charts(self,symbol,exchange_segment,instrument_type,expiry_code,from_date,to_date):
        """Retrieve OHLC & Volume of daily candle for desired instrument. The data for any scrip is available back upto the date of its inception."""
        try:
            url= self.base_url+f'/charts/historical'
            payload= {
                    "symbol": symbol,
                    "exchangeSegment": exchange_segment,
                    "instrument": instrument_type,
                    "expiryCode": expiry_code,
                    "fromDate": from_date,
                    "toDate": to_date
                    }
            payload= json_dumps(payload)
            response= self.session.post(url,headers=self.header,timeout=self.timeout,data=payload)
            return self._parse_response(response)
        except Exception as e:
            logging.error('Exception in dhanhq>>intraday_history_minute_charts: %s',e)
            return {
                'status':'failure',
                'remarks':str(e),
                'data':'',
            }

    def get_trade_book(self,order_id=None):
        """Retrieve a list of all trades executed in a day."""
        try:
            if order_id==None:
                url= self.base_url+f'/trades'
            else:
                url= self.base_url+f'/trades/{order_id}'
            response= self.session.get(url,headers=self.header,timeout=self.timeout)
            return self._parse_response(response)
        except Exception as e:
            logging.error('Exception in dhanhq>>get_trade_book: %s',e)
            return {
                'status':'failure',
                'remarks':str(e),
                'data':'',
            }

    def get_trade_history(self,from_date,to_date,page_number=0):
        """Retrieve the trade history Often during partial trades or Bracket/ Cover Orders, traders get confused in reading trade from tradebook. The response of this API will include all the trades generated for a particular order id."""
        try:
            url= self.base_url+f'/tradeHistory/{from_date}/{to_date}/{page_number}'
            response= self.session.get(url,headers=self.header,timeout=self.timeout)
            return self._parse_response(response)
        except Exception as e:
            logging.error('Exception in dhanhq>>get_trade_history: %s',e)
            return {
                'status':'failure',
                'remarks':str(e),
                'data':'',
            }

    def get_fund_limits(self):
        """Get all information of your trading account like balance, margin utilised, collateral, etc."""
        try:
            url= self.base_url+f'/fundlimit'
            response= self.session.get(url,headers=self.header,timeout=self.timeout)
            return self._parse_response(response)
        except Exception as e:
            logging.error('Exception in dhanhq>>get_fund_limits: %s',e)
            return {
                'status':'failure',
                'remarks':str(e),
                'data':'',
            }
