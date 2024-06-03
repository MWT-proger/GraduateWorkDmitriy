from merlion.utils.time_series import TimeSeries

from schemas.base import TimeseriesSchema


def serializer_timeseries_to_pydantic(ts: TimeSeries) -> TimeseriesSchema:
    """Преобразовать merlion TimeSeries в схему pydantic"""
    if ts is None:
        return None
    df = ts.to_pd()
    return TimeseriesSchema(
        data=df.to_dict(orient="list"), index=df.index.tolist()
    )
