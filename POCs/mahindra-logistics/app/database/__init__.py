import pandas as pd
from app.common.utils import stop_watch
from datetime import datetime

@stop_watch
def result_tracker(success, url, data=None,error=None):
    try:
        x = pd.read_csv('tracking.csv')
    except Exception as e:
        x = pd.DataFrame()
    now = datetime.utcnow().isoformat()
    if data:
        result = [[url, success, data['classified_as'], data['lr_number'], None, now]]
    else:
        result = [[url, success, None, None, error, now]]
    df = pd.DataFrame(columns=['url', 'success', 'classified_as', 'lr_number', 'error', 'at'], data=result)
    x = pd.concat([x, df])
    x.to_csv('tracking.csv', index=False)
    