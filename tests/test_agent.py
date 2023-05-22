from EV.agent import EV
from EV.model import EVModel
import EV.model_config as cfg

from pytest import MonkeyPatch

def test_EV_set_ev_consumption_rate_nonzero() -> None:
    test = EV(unique_id=1, model=EVModel(
        ticks=cfg.ticks, 
        no_evs=cfg.no_evs, 
        station_params=cfg.station_config, 
        location_params=cfg.location_config, 
        station_location_param=cfg.station_location_config, 
        overnight_charging=cfg.overnight_charging,
        grid_height=cfg.grid_height,
        grid_width=cfg.grid_width
    ))
    test.set_ev_consumption_rate()
    assert test.ev_consumption_rate != 0

def test_EV_set_ev_consumption_rate_upper_bound() -> None:
    test = EV(unique_id=1, model=EVModel(
        ticks=cfg.ticks, 
        no_evs=cfg.no_evs, 
        station_params=cfg.station_config, 
        location_params=cfg.location_config, 
        station_location_param=cfg.station_location_config, 
        overnight_charging=cfg.overnight_charging,
        grid_height=cfg.grid_height,
        grid_width=cfg.grid_width
    ))
    test.set_ev_consumption_rate()
    assert test.ev_consumption_rate < 0.7

def test_EV_set_ev_consumption_rate_lower_bound() -> None:
    test = EV(unique_id=1, model=EVModel(
        ticks=cfg.ticks, 
        no_evs=cfg.no_evs, 
        station_params=cfg.station_config, 
        location_params=cfg.location_config, 
        station_location_param=cfg.station_location_config, 
        overnight_charging=cfg.overnight_charging,
        grid_height=cfg.grid_height,
        grid_width=cfg.grid_width
    ))
    test.set_ev_consumption_rate()
    assert test.ev_consumption_rate > 0.3


def test_EV_energy_usage_trip_nonzero() -> None:
    test = EV(unique_id=1, model=EVModel(
        ticks=cfg.ticks, 
        no_evs=cfg.no_evs, 
        station_params=cfg.station_config, 
        location_params=cfg.location_config, 
        station_location_param=cfg.station_location_config, 
        overnight_charging=cfg.overnight_charging,
        grid_height=cfg.grid_height,
        grid_width=cfg.grid_width
    ))
    test.odometer = 100
    test.ev_consumption_rate = 0.62

    value = test.energy_usage_trip()
    assert value != 0

def test_EV_energy_usage_trip() -> None:
    test = EV(unique_id=1, model=EVModel(
        ticks=cfg.ticks, 
        no_evs=cfg.no_evs, 
        station_params=cfg.station_config, 
        location_params=cfg.location_config, 
        station_location_param=cfg.station_location_config, 
        overnight_charging=cfg.overnight_charging,
        grid_height=cfg.grid_height,
        grid_width=cfg.grid_width
    ))
    test.odometer = 100
    test.ev_consumption_rate = 0.62
    value = test.energy_usage_trip()
    assert value == 62

def test_EV_energy_usage_tick_nonzero() -> None:
    test = EV(unique_id=1, model=EVModel(
        ticks=cfg.ticks, 
        no_evs=cfg.no_evs, 
        station_params=cfg.station_config, 
        location_params=cfg.location_config, 
        station_location_param=cfg.station_location_config, 
        overnight_charging=cfg.overnight_charging,
        grid_height=cfg.grid_height,
        grid_width=cfg.grid_width
    ))
    test._speed = 25
    test.ev_consumption_rate = 0.62

    value = test.energy_usage_tick()
    assert value != 0

def test_EV_energy_usage_tick() -> None:
    test = EV(unique_id=1, model=EVModel(
        ticks=cfg.ticks, 
        no_evs=cfg.no_evs, 
        station_params=cfg.station_config, 
        location_params=cfg.location_config, 
        station_location_param=cfg.station_location_config, 
        overnight_charging=cfg.overnight_charging,
        grid_height=cfg.grid_height,
        grid_width=cfg.grid_width
    ))
    test._speed = 25
    test.ev_consumption_rate = 0.66
    value = test.energy_usage_tick()
    assert value == 16.5


# def test_agent_park() -> None:
#     with pytest.raises(AttributeError):
#         test = EV(unique_id=1, model=EVModel(
#             ticks=cfg.ticks, 
#             no_evs=cfg.no_evs, 
#             station_params=cfg.station_config, 
#             location_params=cfg.location_config, 
#             station_location_param=cfg.station_location_config, 
#             overnight_charging=cfg.overnight_charging,
#             grid_height=cfg.grid_height,
#             grid_width=cfg.grid_width
#         ))
#         test.park()

# # Monkeypatching for testing. Managing user input to test structure.
# def test_agent_park(monkeypatch: MonkeyPatch) -> None:
#     inputs = ["0", "1", "2", "3", "4"]
#     monkeypatch.setattr("builtins.input", lambda _: inputs.pop())
#     monkeypatch.setattr(Class, "attr", lambda _: True)   
#     test = EV(unique_id=1, model=EVModel(
#         ticks=cfg.ticks,
#         no_evs=cfg.no_evs,
#         station_params=cfg.station_config,
#         location_params=cfg.location_config,
#         station_location_param=cfg.station_location_config,
#         overnight_charging=cfg.overnight_charging,
#         grid_height=cfg.grid_height,
#         grid_width=cfg.grid_width
#     ))
#     test.park()
#     assert test._is_parked == True
