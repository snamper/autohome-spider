class Brand(object):
    def __init__(self, brand_id, brand_name, brand_first_letter, brand_logo):
        """
        :type brand_id: int
        :type brand_name: str
        :type brand_first_letter: str
        :type brand_logo: str
        """
        self.brand_id = brand_id
        self.brand_name = brand_name.strip()
        self.brand_first_letter = brand_first_letter.strip()
        self.brand_logo = brand_logo.strip()

    def __eq__(self, other):
        return self.brand_id == other.brand_id


class Factory(object):
    def __init__(self, factory_id, factory_name, factory_first_letter, brand):
        """
        :type factory_id: int
        :type factory_name: str
        :type factory_first_letter: str
        :type brand: Brand
        """
        self.factory_id = factory_id
        self.factory_name = factory_name.strip()
        self.factory_first_letter = factory_first_letter.strip()
        self.brand = brand

    def __eq__(self, other):
        return self.factory_id == other.factory_id


class Series(object):
    def __init__(self, series_id, series_name, series_first_letter,
                 series_state, series_order, factory, brand=None):
        """
        :type series_id: int
        :type series_name: str
        :type series_first_letter: str
        :type series_state: int
        :type series_order: int
        :type factory: Factory
        :type brand: Brand
        """
        self.series_id = series_id
        self.series_name = series_name.strip()
        self.series_first_letter = series_first_letter.strip()
        self.series_state = series_state
        self.series_order = series_order
        self.factory = factory
        self.brand = brand or factory.brand

    def __eq__(self, other):
        return self.series_id == other.series_id


class Spec(object):
    __slots__ = (
        'spec_id', 'spec_name', 'spec_year_name', 'spec_state',
        'spec_min_price', 'spec_max_price', 'series', 'factory', 'brand',
        'level', 'energy_type', 'marketed_time', 'gearbox', 'length', 'width',
        'height', 'max_speed', 'official_acceleration', 'gearbox_type',
        'measured_acceleration', 'measured_hrake', 'official_fuel_consumption',
        'measured_fuel_consumption', 'vehicle_warranty', 'wheelbase',
        'front_track', 'rear_track', 'min_ground_clearance', 'body_structure',
        'doors', 'seats', 'tank_volume', 'luggage_compartment_volume',
        'weight', 'displacement', 'intake_form', 'cylinder_arrangement',
        'cylinders', 'valves_per_cylinder', 'compression_ratio',
        'gas_distribution_mechanism', 'cylinder_diameter', 'cylinder_stroke',
        'max_horsepower', 'max_power', 'max_power_speed', 'max_torque',
        'max_torque_speed', 'engine_specific_technology', 'fuel_form',
        'fuel_grade', 'fuel_supply_mode', 'cylinder_head_material',
        'cylinder_material', 'environmental_standards', 'rear_suspension_type',
        'assist_type', 'body_structure2', 'brake_type', 'real_brake_type',
        'guide_price', 'front_tire_specification', 'rear_tire_specification',
        'spare_tire_specifications', 'main_airbag', 'co_airbag',
        'front_side_airbag', 'rear_side_airbag', 'front_head_airbag',
        'rear_head_airbag', 'knee_airbag', 'tire_pressure',
        'zero_tire_pressure', 'zero_tire_pressure_continues', 'isofix', 'abs',
        'brake_power_distribution', 'brake_assist', 'traction_control',
        'body_stability_control', 'parallel_assist',
        'lane_departure_warning_system', 'active_brake_or_safety_system',
        'night_vision_system', 'fatigue_driving_tips', 'front_parking_radar',
        'rear_parking_radar', 'driving_assistance_image', 'cruise_system',
        'driving_mode_switching', 'automatic_parking_entry',
        'engine_start_stop_technology', 'automatic_parking', 'uphill_assist',
        'steep_slope', 'variable_suspension_function', 'air_suspension',
        'electromagnetic_induction_suspension', 'variable_steering_ratio',
        'central_differential_lock_function', 'overall_active_steering_system',
        'limited_slip_differential_differential_lock', 'sunroof_type',
        'sports_look_kit', 'wheel_material', 'electric_suction_door',
        'side_sliding_door_form', 'electric_trunk', 'induction_trunk',
        'roof_rack', 'engine_electronic_anti_theft',
        'central_locking_in_the_car', 'key_type', 'keyless_start_system',
        'keyless_entry', 'remote_start_function', 'side_pedal',
        'steering_wheel_material', 'steering_wheel_position_adjustment',
        'multifunction_steering_wheel', 'steering_wheel_shift',
        'steering_wheel_heating', 'steering_wheel_memory',
        'driving_computer_display_screen', 'full_lcd_instrument_panel',
        'lcd_meter_size', 'hud_head_up_digital_display',
        'builtin_driving_recorder', 'active_noise_reduction',
        'mobile_phone_wireless_charging_function', 'seat_material',
        'sporty_seat', 'main_seat_adjustment', 'sub_seat_adjustment',
        'main_driver_electric_adjustment', 'co_driver_electric_adjustment',
        'front_seat_function', 'electric_seat_memory_function',
        'rear_passenger_seat_adjustable_button', 'second_row_seat_adjustment',
        'rear_seat_electric_adjustment', 'rear_seat_function',
        'second_row_of_independent_seats', 'seat_layout', 'rear_seat_down',
        'front_central_armrest', 'rear_central_armrest', 'rear_cup_holder',
        'heating_or_cooling_cup_holder', 'central_control_color_lcd_screen',
        'central_control_lcd_screen_size', 'gps_navigation_system',
        'road_rescue_call', 'central_control_lcd_screen_display',
        'bluetooth_or_mobile', 'mobile_interconnection',
        'speech_recognition_control_system', 'car_networking', 'car_tv',
        'rear_lcd_screen', 'external_audio_interface_type',
        'usb_or_typec_interfaces', 'car_dvd', 'power_supply',
        'speaker_brand_name', 'speakers', 'low_beam_light_source',
        'high_beam_light_source', 'lighting_features',
        'led_daytime_running_lights', 'adaptive_far_and_near_light',
        'automatic_headlight', 'steering_auxiliary_light',
        'steering_headlight', 'front_fog_light', 'headlight_rain_fog_mode',
        'headlight_height_adjustable', 'headlight_cleaning_device',
        'headlight_delay_off', 'touch_reading_light',
        'interior_environment_atmosphere_lamp', 'front_power_window',
        'rear_power_window', 'window_one_button_lifting_function',
        'window_anti_pinch_function', 'multi_layer_acoustic_glass',
        'exterior_mirror_function', 'interior_mirror_function',
        'rear_windshield_sunshade', 'rear_side_window_sunshade',
        'rear_side_privacy_glass', 'interior_mirror', 'rear_wiper',
        'induction_wiper_function', 'max_load_mass', 'container_size',
        'air_conditioning_temperature_control_method',
        'rear_independent_air_conditioner', 'rear_seat_outlet',
        'temperature_zone_control', 'air_purifier', 'refrigerator',
        'central_differential_structure', 'front_suspension_type',
        'rear_belt_airbag', 'rear_central_airbag',
        'passive_pedestrian_protection', 'lane_keeping_assist_system',
        'road_traffic_identification', 'reverse_side_warning_system',
        'water_sensing_system', 'electric_trunk_position_memory',
        'the_tailgate_glass_is_opened_independently',
        'active_closed_intake_grille', 'battery_preheating',
        'electric_adjustable_pedal', 'navigation_traffic_information_display',
        'gesture_control', 'ota_upgrade', 'rear_control_multimedia',
        'luggage_compartment_12V_power_interface', 'heatable_water_spout',
        'pm25_filter_unit', 'negative_ion_generator', 'rear_door_opening_mode',
        'interior_fragrance_device', 'rear_table', 'rear_seat_electric_down',
        'motor_total_torque', 'motor_front_max_power', 'motor_total_power',
        'motor_front_max_torque', 'motor_rear_max_power',
        'motor_rear_max_torque', 'motor_comprehensive_power',
        'motor_comprehensive_torque', 'motors', 'motor_layout', 'battery_type',
        'fast_charging_time', 'slow_charging_time', 'measured_range',
        'measured_fast_charging_time', 'measured_slow_charging_time',
        'battery_capacity', 'power_consumption', 'battery_pack_warranty',
        'battery_charging_time', 'fast_charge', 'official_range',
    )

    def __init__(self, spec_id, spec_name, spec_year_name, spec_state,
                 spec_min_price, spec_max_price, series, factory=None,
                 brand=None):
        """
        :type spec_id: int
        :type spec_name: str
        :type spec_year_name:
        :type spec_state: int
        :type spec_min_price: int
        :type spec_max_price: int
        :type series: Series
        :type factory: Factory
        :type brand: Brand
        """
        self.spec_id = spec_id
        self.spec_name = spec_name.strip()
        self.spec_year_name = spec_year_name.strip()
        self.spec_state = spec_state
        self.spec_min_price = spec_min_price
        self.spec_max_price = spec_max_price
        self.series = series
        self.factory = factory or series.factory
        self.brand = brand or series.brand

    def __eq__(self, other):
        return self.spec_id == other.spec_id
