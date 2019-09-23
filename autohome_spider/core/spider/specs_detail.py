import os
import re

import copy
import requests
from bs4 import BeautifulSoup, Tag

from .specs import SpecsSpider
from ..structure import Spec


class SpecsDetailSpider(object):
    """
    爬取车型详细数据。
    """
    url_tpl = 'https://dealer.autohome.com.cn/Price/_SpecConfig?SpecId={spec_id}'
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }

    def __init__(self, specs=None):
        """
        :type specs: list[Spec]
        """
        self._specs = specs

    @property
    def specs(self):
        specs = self._specs
        if specs is None:
            spider = SpecsSpider()
            specs = spider.specs

        with requests.session() as req:
            for spec in specs:
                spec_path = 'downloads/spec-%s.html' % spec.spec_id
                if os.path.exists(spec_path):
                    with open(spec_path) as f:
                        html = f.read()
                else:
                    url = self.url_tpl.format(spec_id=spec.spec_id)
                    resp = req.get(url, headers=self.headers)
                    if resp.status_code != 200:
                        continue
                    html = resp.content.decode('gbk')
                    with open(spec_path, 'w+') as f:
                        f.write(html)
                spec = self.parse_html(html, copy.copy(spec))
                yield spec

    @classmethod
    def parse_html(cls, html, spec):
        """
        :type html: str
        :type spec: Spec
        :rtype: Spec
        """
        bs = BeautifulSoup(html, 'html.parser')
        for _ in bs.select('div.tabcont-cont'):
            for __ in _.select('div.config'):
                if __['id'] not in ('tab-10', 'tab-11'):
                    continue
                cur_group = ''
                for ___ in __.children:
                    if not isinstance(___, Tag):
                        continue
                    if 'config-title' in ___['class']:
                        cur_group = ___.text.strip()
                    elif 'config-cont' in ___['class']:
                        SpecParser(___, spec, cur_group).parse()
        return spec


class SpecParser(object):
    default_parser = 'parse_none'
    parsers = {
        '基本参数': 'parse_base',
        '车身': 'parse_body',
        '发动机': 'parse_engine',
        '变速箱': 'parse_gearbox',
        '底盘转向': 'parse_base_plate',
        '车轮制动': 'parse_parking',
        '主/被动安全装备': 'parse_safety',
        '辅助/操控配置': 'parse_assist',
        '外部/防盗配置': 'parse_outside',
        '内部配置': 'parse_inside',
        '座椅配置': 'parse_seats',
        '多媒体配置': 'parse_media',
        '灯光配置': 'parse_light',
        '玻璃/后视镜': 'parse_glass',
        '空调/冰箱': 'parse_temperature',
        '电动机': 'parse_motor',
    }
    default_ignore_props = ('-',)
    ignore_props = {
        '基本参数': ('-', '厂商', '环保标准', '最大功率(kW)', '最大扭矩(N·m)',
                 '发动机', '车身结构', '变速箱', '快充电量百分比', '快充时间(小时)',
                 '慢充时间(小时)', '工信部纯电续航里程(km)',),
    }

    def __init__(self, tag, spec, group):
        """
        :type tag: Tag
        :type spec: Spec
        :type group: str
        """
        self.tag = tag
        self.spec = spec
        self.group = group
        self.un_parse_props = []

    def parse(self):
        for tr in self.tag.select('table.config-table tbody tr'):
            prop = ''
            for _ in tr.find_all(re.compile('^t.')):
                if _.name == 'th':
                    prop = _.text.strip()
                elif _.name == 'td':
                    value = _.text.strip()
                    parser = self.parsers.get(self.group, self.default_parser)
                    getattr(self, parser)(prop, value)
        if len(self.un_parse_props) > 0:
            print(self.group, self.un_parse_props)

    def parse_none(self, prop, value):
        """
        :type prop: str
        :type value: str
        """
        ignore_props = self.ignore_props.get(
            self.group, self.default_ignore_props)
        if prop not in ignore_props:
            self.un_parse_props.append(prop)

    def parse_base(self, prop, value):
        """
        :type prop: str
        :type value: str
        """
        ignore_props = self.ignore_props.get(
            self.group, self.default_ignore_props)
        spec = self.spec
        if prop in ignore_props:
            pass
        elif prop == '级别':
            spec.level = value
        elif prop == '能源类型':
            spec.energy_type = value
        elif prop == '上市时间':
            spec.marketed_time = value
        elif prop == '厂商指导价(元)':
            spec.guide_price = value
        elif prop == '长*宽*高(mm)':
            _tmp = value.split('*') + ['', '']
            try:
                spec.length = int(_tmp[0])
                spec.width = int(_tmp[1])
                spec.height = int(_tmp[2])
            except ValueError:
                spec.length = spec.width = spec.height = -1
        elif prop == '最高车速(km/h)':
            spec.max_speed = value
        elif prop == '官方0-100km/h加速(s)':
            spec.official_acceleration = value
        elif prop == '实测0-100km/h加速(s)':
            spec.measured_acceleration = value
        elif prop == '实测100-0km/h制动(m)':
            spec.measured_hrake = value
        elif prop == '工信部综合油耗(L/100km)':
            spec.official_fuel_consumption = value
        elif prop == '实测油耗(L/100km)':
            spec.measured_fuel_consumption = value
        elif prop == '整车质保':
            spec.vehicle_warranty = value
        elif prop == '实测续航里程(km)':
            spec.measured_range = value
        elif prop == '实测快充时间(小时)':
            spec.measured_fast_charging_time = value
        elif prop == '实测慢充时间(小时)':
            spec.measured_slow_charging_time = value
        else:
            self.un_parse_props.append(prop)

    def parse_body(self, prop, value):
        """
        :type prop: str
        :type value: str
        """
        ignore_props = self.ignore_props.get(
            self.group, self.default_ignore_props)
        spec = self.spec
        if prop in ignore_props:
            pass
        elif prop == '高度(mm)':
            spec.height = value
        elif prop == '宽度(mm)':
            spec.width = value
        elif prop == '轴距(mm)':
            spec.wheelbase = value
        elif prop == '前轮距(mm)':
            spec.front_track = value
        elif prop == '后轮距(mm)':
            spec.rear_track = value
        elif prop == '最小离地间隙(mm)':
            spec.min_ground_clearance = value
        elif prop == '车身结构':
            spec.body_structure = value
        elif prop == '车门数(个)':
            spec.doors = value
        elif prop == '座位数(个)':
            spec.seats = value
        elif prop == '油箱容积(L)':
            spec.tank_volume = value
        elif prop == '行李厢容积(L)':
            spec.luggage_compartment_volume = value
        elif prop == '整备质量(kg)':
            spec.weight = value
        elif prop == '最大载重质量(kg)':
            spec.max_load_mass = value
        elif prop == '货箱尺寸(mm)':
            spec.container_size = value
        elif prop == '后排车门开启方式':
            spec.rear_door_opening_mode = value
        else:
            self.un_parse_props.append(prop)

    def parse_engine(self, prop, value):
        """
        :type prop: str
        :type value: str
        """
        ignore_props = self.ignore_props.get(
            self.group, self.default_ignore_props)
        spec = self.spec
        if prop in ignore_props:
            pass
        elif prop == '排量(L)':
            spec.displacement = value
        elif prop == '排量(mL)':
            try:
                spec.displacement = float(value) / 1000
            except ValueError:
                pass
        elif prop == '进气形式':
            spec.intake_form = value
        elif prop == '气缸排列形式':
            spec.cylinder_arrangement = value
        elif prop == '气缸数(个)':
            spec.cylinders = value
        elif prop == '每缸气门数(个)':
            spec.valves_per_cylinder = value
        elif prop == '压缩比':
            spec.compression_ratio = value
        elif prop == '配气机构':
            spec.gas_distribution_mechanism = value
        elif prop == '缸径(mm)':
            spec.cylinder_diameter = value
        elif prop == '行程(mm)':
            spec.cylinder_stroke = value
        elif prop == '最大马力(Ps)':
            spec.max_horsepower = value
        elif prop == '最大功率(kW)':
            spec.max_power = value
        elif prop == '最大功率转速(rpm)':
            spec.max_power_speed = value
        elif prop == '最大扭矩(N·m)':
            spec.max_torque = value
        elif prop == '最大扭矩转速(rpm)':
            spec.max_torque_speed = value
        elif prop == '发动机特有技术':
            spec.engine_specific_technology = value
        elif prop == '燃料形式':
            spec.fuel_form = value
        elif prop == '燃油标号':
            spec.fuel_grade = value
        elif prop == '供油方式':
            spec.fuel_supply_mode = value
        elif prop == '缸盖材料':
            spec.cylinder_head_material = value
        elif prop == '缸体材料':
            spec.cylinder_material = value
        elif prop == '环保标准':
            spec.environmental_standards = value
        else:
            self.un_parse_props.append(prop)

    def parse_gearbox(self, prop, value):
        """
        :type prop: str
        :type value: str
        """
        ignore_props = self.ignore_props.get(
            self.group, self.default_ignore_props)
        spec = self.spec
        if prop in ignore_props:
            pass
        elif prop == '简称':
            spec.gearbox = value
        elif prop == '变速箱类型':
            spec.gearbox_type = value
        else:
            self.un_parse_props.append(prop)

    def parse_base_plate(self, prop, value):
        """
        :type prop: str
        :type value: str
        """
        ignore_props = self.ignore_props.get(
            self.group, self.default_ignore_props)
        spec = self.spec
        if prop in ignore_props:
            pass
        elif prop == '后悬架类型':
            spec.rear_suspension_type = value
        elif prop == '助力类型':
            spec.assist_type = value
        elif prop == '车体结构':
            spec.body_structure2 = value
        elif prop == '中央差速器结构':
            spec.central_differential_structure = value
        elif prop == '前悬架类型':
            spec.front_suspension_type = value
        else:
            self.un_parse_props.append(prop)

    def parse_parking(self, prop, value):
        """
        :type prop: str
        :type value: str
        """
        ignore_props = self.ignore_props.get(
            self.group, self.default_ignore_props)
        spec = self.spec
        if prop in ignore_props:
            pass
        elif prop == '驻车制动类型':
            spec.brake_type = value
        elif prop == '后制动器类型':
            spec.real_brake_type = value
        elif prop == '前轮胎规格':
            spec.front_tire_specification = value
        elif prop == '后轮胎规格':
            spec.rear_tire_specification = value
        elif prop == '备胎规格':
            spec.spare_tire_specifications = value
        else:
            self.un_parse_props.append(prop)

    def parse_safety(self, prop, value):
        """
        :type prop: str
        :type value: str
        """
        ignore_props = self.ignore_props.get(
            self.group, self.default_ignore_props)
        spec = self.spec
        if prop in ignore_props:
            pass
        elif prop == '主/副驾驶座安全气囊':
            _tmp = value.split('/') + ['']
            spec.main_airbag = _tmp[0].replace('主', '').strip()
            spec.co_airbag = _tmp[1].replace('副', '').strip()
        elif prop == '前/后排侧气囊':
            _tmp = value.split('/') + ['']
            spec.front_side_airbag = _tmp[0].replace(
                '前', '').strip()
            spec.rear_side_airbag = _tmp[1].replace(
                '后', '').strip()
        elif prop == '前/后排头部气囊(气帘)':
            _tmp = value.split('/') + ['']
            spec.front_head_airbag = _tmp[0].replace(
                '前', '').strip()
            spec.rear_head_airbag = _tmp[1].replace(
                '后', '').strip()
        elif prop == '后排安全带式气囊':
            spec.rear_belt_airbag = value
        elif prop == '后排中央安全气囊':
            spec.rear_central_airbag = value
        elif prop == '被动行人保护':
            spec.passive_pedestrian_protection = value
        elif prop == '车道保持辅助系统':
            spec.lane_keeping_assist_system = value
        elif prop == '道路交通标识识别':
            spec.road_traffic_identification = value
        elif prop == '膝部气囊':
            spec.knee_airbag = value
        elif prop == '胎压监测功能':
            spec.tire_pressure = value
        elif prop == '零胎压继续行驶':
            spec.zero_tire_pressure = value
        elif prop == '安全带未系提醒':
            spec.zero_tire_pressure_continues = value
        elif prop == 'ISOFIX儿童座椅接口':
            spec.isofix = value
        elif prop == 'ABS防抱死':
            spec.abs = value
        elif prop == '制动力分配(EBD/CBC等)':
            spec.brake_power_distribution = value
        elif prop == '刹车辅助(EBA/BAS/BA等)':
            spec.brake_assist = value
        elif prop == '牵引力控制(ASR/TCS/TRC等)':
            spec.traction_control = value
        elif prop == '车身稳定控制(ESC/ESP/DSC等)':
            spec.body_stability_control = value
        elif prop == '并线辅助':
            spec.parallel_assist = value
        elif prop == '车道偏离预警系统':
            spec.lane_departure_warning_system = value
        elif prop == '主动刹车/主动安全系统':
            spec.active_brake_or_safety_system = value
        elif prop == '夜视系统':
            spec.night_vision_system = value
        elif prop == '疲劳驾驶提示':
            spec.fatigue_driving_tips = value
        else:
            self.un_parse_props.append(prop)

    def parse_assist(self, prop, value):
        """
        :type prop: str
        :type value: str
        """
        ignore_props = self.ignore_props.get(
            self.group, self.default_ignore_props)
        spec = self.spec
        if prop in ignore_props:
            pass
        elif prop == '前/后驻车雷达':
            _tmp = value.split('/') + ['']
            spec.front_parking_radar = _tmp[0].replace(
                '前', '').strip()
            spec.rear_parking_radar = _tmp[1].replace(
                '后', '').strip()
        elif prop == '驾驶辅助影像':
            spec.driving_assistance_image = value
        elif prop == '倒车车侧预警系统':
            spec.reverse_side_warning_system = value
        elif prop == '涉水感应系统':
            spec.water_sensing_system = value
        elif prop == '巡航系统':
            spec.cruise_system = value
        elif prop == '驾驶模式切换':
            spec.driving_mode_switching = value
        elif prop == '自动泊车入位':
            spec.automatic_parking_entry = value
        elif prop == '发动机启停技术':
            spec.engine_start_stop_technology = value
        elif prop == '自动驻车':
            spec.automatic_parking = value
        elif prop == '上坡辅助':
            spec.uphill_assist = value
        elif prop == '陡坡缓降':
            spec.steep_slope = value
        elif prop == '可变悬架功能':
            spec.variable_suspension_function = value
        elif prop == '空气悬架':
            spec.air_suspension = value
        elif prop == '电磁感应悬架':
            spec.electromagnetic_induction_suspension = value
        elif prop == '可变转向比':
            spec.variable_steering_ratio = value
        elif prop == '中央差速器锁止功能':
            spec.central_differential_lock_function = value
        elif prop == '整体主动转向系统':
            spec.overall_active_steering_system = value
        elif prop == '限滑差速器/差速锁':
            spec.limited_slip_differential_differential_lock = value
        else:
            self.un_parse_props.append(prop)

    def parse_outside(self, prop, value):
        """
        :type prop: str
        :type value: str
        """
        ignore_props = self.ignore_props.get(
            self.group, self.default_ignore_props)
        spec = self.spec
        if prop in ignore_props:
            pass
        elif prop == '天窗类型':
            spec.sunroof_type = value
        elif prop == '运动外观套件':
            spec.sports_look_kit = value
        elif prop == '轮圈材质':
            spec.wheel_material = value
        elif prop == '电动吸合车门':
            spec.electric_suction_door = value
        elif prop == '侧滑门形式':
            spec.side_sliding_door_form = value
        elif prop == '电动后备厢':
            spec.electric_trunk = value
        elif prop == '电动后备厢位置记忆':
            spec.electric_trunk_position_memory = value
        elif prop == '尾门玻璃独立开启':
            spec.the_tailgate_glass_is_opened_independently = value
        elif prop == '主动闭合式进气格栅':
            spec.active_closed_intake_grille = value
        elif prop == '电池预加热':
            spec.battery_preheating = value
        elif prop == '感应后备厢':
            spec.induction_trunk = value
        elif prop == '车顶行李架':
            spec.roof_rack = value
        elif prop == '发动机电子防盗':
            spec.engine_electronic_anti_theft = value
        elif prop == '车内中控锁':
            spec.central_locking_in_the_car = value
        elif prop == '钥匙类型':
            spec.key_type = value
        elif prop == '无钥匙启动系统':
            spec.keyless_start_system = value
        elif prop == '无钥匙进入功能':
            spec.keyless_entry = value
        elif prop == '远程启动功能':
            spec.remote_start_function = value
        elif prop == '车侧脚踏板':
            spec.side_pedal = value
        else:
            self.un_parse_props.append(prop)

    def parse_inside(self, prop, value):
        """
        :type prop: str
        :type value: str
        """
        ignore_props = self.ignore_props.get(
            self.group, self.default_ignore_props)
        spec = self.spec
        if prop in ignore_props:
            pass
        elif prop == '方向盘材质':
            spec.steering_wheel_material = value
        elif prop == '方向盘位置调节':
            spec.steering_wheel_position_adjustment = value
        elif prop == '多功能方向盘':
            spec.multifunction_steering_wheel = value
        elif prop == '方向盘换挡':
            spec.steering_wheel_shift = value
        elif prop == '电动可调踏板':
            spec.electric_adjustable_pedal = value
        elif prop == '方向盘加热':
            spec.steering_wheel_heating = value
        elif prop == '方向盘记忆':
            spec.steering_wheel_memory = value
        elif prop == '行车电脑显示屏幕':
            spec.driving_computer_display_screen = value
        elif prop == '全液晶仪表盘':
            spec.full_lcd_instrument_panel = value
        elif prop == '液晶仪表尺寸':
            spec.lcd_meter_size = value
        elif prop == 'HUD抬头数字显示':
            spec.hud_head_up_digital_display = value
        elif prop == '内置行车记录仪':
            spec.builtin_driving_recorder = value
        elif prop == '主动降噪':
            spec.active_noise_reduction = value
        elif prop == '手机无线充电功能':
            spec.mobile_phone_wireless_charging_function = value
        else:
            self.un_parse_props.append(prop)

    def parse_seats(self, prop, value):
        """
        :type prop: str
        :type value: str
        """
        ignore_props = self.ignore_props.get(
            self.group, self.default_ignore_props)
        spec = self.spec
        if prop in ignore_props:
            pass
        elif prop == '座椅材质':
            spec.seat_material = value
        elif prop == '运动风格座椅':
            spec.sporty_seat = value
        elif prop == '主座椅调节方式':
            spec.main_seat_adjustment = value
        elif prop == '副座椅调节方式':
            spec.sub_seat_adjustment = value
        elif prop == '主/副驾驶座电动调节':
            _tmp = value.split('/') + ['']
            spec.main_driver_electric_adjustment = _tmp[0].replace(
                '主', '').strip()
            spec.co_driver_electric_adjustment = _tmp[1].replace(
                '副', '').strip()
        elif prop == '前排座椅功能':
            spec.front_seat_function = value
        elif prop == '电动座椅记忆功能':
            spec.electric_seat_memory_function = value
        elif prop == '副驾驶位后排可调节按钮':
            spec.rear_passenger_seat_adjustable_button = value
        elif prop == '第二排座椅调节':
            spec.second_row_seat_adjustment = value
        elif prop == '后排座椅电动调节':
            spec.rear_seat_electric_adjustment = value
        elif prop == '后排座椅功能':
            spec.rear_seat_function = value
        elif prop == '第二排独立座椅':
            spec.second_row_of_independent_seats = value
        elif prop == '座椅布局':
            spec.seat_layout = value
        elif prop == '后排小桌板':
            spec.rear_table = value
        elif prop == '后排座椅电动放倒':
            spec.rear_seat_electric_down = value
        elif prop == '后排座椅放倒形式':
            spec.rear_seat_down = value
        elif prop == '前/后中央扶手':
            _tmp = value.split('/') + ['']
            spec.front_central_armrest = _tmp[0].replace(
                '前', '').strip()
            spec.rear_central_armrest = _tmp[1].replace(
                '后', '').strip()
        elif prop == '后排杯架':
            spec.rear_cup_holder = value
        elif prop == '加热/制冷杯架':
            spec.heating_or_cooling_cup_holder = value
        else:
            self.un_parse_props.append(prop)

    def parse_media(self, prop, value):
        """
        :type prop: str
        :type value: str
        """
        ignore_props = self.ignore_props.get(
            self.group, self.default_ignore_props)
        spec = self.spec
        if prop in ignore_props:
            pass
        elif prop == '中控彩色液晶屏幕':
            spec.central_control_color_lcd_screen = value
        elif prop == '中控液晶屏尺寸':
            spec.central_control_lcd_screen_size = value
        elif prop == 'GPS导航系统':
            spec.gps_navigation_system = value
        elif prop == '道路救援呼叫':
            spec.road_rescue_call = value
        elif prop == '中控液晶屏分屏显示':
            spec.central_control_lcd_screen_display = value
        elif prop == '蓝牙/车载电话':
            spec.bluetooth_or_mobile = value
        elif prop == '手机互联/映射':
            spec.mobile_interconnection = value
        elif prop == '导航路况信息显示':
            spec.navigation_traffic_information_display = value
        elif prop == '手势控制':
            spec.gesture_control = value
        elif prop == 'OTA升级':
            spec.ota_upgrade = value
        elif prop == '后排控制多媒体':
            spec.rear_control_multimedia = value
        elif prop == '行李厢12V电源接口':
            spec.luggage_compartment_12V_power_interface = value
        elif prop == '语音识别控制系统':
            spec.speech_recognition_control_system = value
        elif prop == '车联网':
            spec.car_networking = value
        elif prop == '车载电视':
            spec.car_tv = value
        elif prop == '后排液晶屏幕':
            spec.rear_lcd_screen = value
        elif prop == '外接音源接口类型':
            spec.external_audio_interface_type = value
        elif prop == 'USB/Type-C接口数量':
            spec.usb_or_typec_interfaces = value
        elif prop == '车载CD/DVD':
            spec.car_dvd = value
        elif prop == '220V/230V电源':
            spec.power_supply = value
        elif prop == '扬声器品牌名称':
            spec.speaker_brand_name = value
        elif prop == '扬声器数量':
            spec.speakers = value
        else:
            self.un_parse_props.append(prop)

    def parse_light(self, prop, value):
        """
        :type prop: str
        :type value: str
        """
        ignore_props = self.ignore_props.get(
            self.group, self.default_ignore_props)
        spec = self.spec
        if prop in ignore_props:
            pass
        elif prop == '近光灯光源':
            spec.low_beam_light_source = value
        elif prop == '远光灯光源':
            spec.high_beam_light_source = value
        elif prop == '灯光特色功能':
            spec.lighting_features = value
        elif prop == 'LED日间行车灯':
            spec.led_daytime_running_lights = value
        elif prop == '自适应远近光':
            spec.adaptive_far_and_near_light = value
        elif prop == '自动头灯':
            spec.automatic_headlight = value
        elif prop == '转向辅助灯':
            spec.steering_auxiliary_light = value
        elif prop == '转向头灯':
            spec.steering_headlight = value
        elif prop == '车前雾灯':
            spec.front_fog_light = value
        elif prop == '前大灯雨雾模式':
            spec.headlight_rain_fog_mode = value
        elif prop == '大灯高度可调':
            spec.headlight_height_adjustable = value
        elif prop == '大灯清洗装置':
            spec.headlight_cleaning_device = value
        elif prop == '大灯延时关闭':
            spec.headlight_delay_off = value
        elif prop == '触摸式阅读灯':
            spec.touch_reading_light = value
        elif prop == '车内环境氛围灯':
            spec.interior_environment_atmosphere_lamp = value
        else:
            self.un_parse_props.append(prop)

    def parse_glass(self, prop, value):
        """
        :type prop: str
        :type value: str
        """
        ignore_props = self.ignore_props.get(
            self.group, self.default_ignore_props)
        spec = self.spec
        if prop in ignore_props:
            pass
        elif prop == '前/后电动车窗':
            spec.front_power_window = value
            spec.rear_power_window = value
        elif prop == '车窗一键升降功能':
            spec.window_one_button_lifting_function = value
        elif prop == '车窗防夹手功能':
            spec.window_anti_pinch_function = value
        elif prop == '可加热喷水嘴':
            spec.heatable_water_spout = value
        elif prop == '多层隔音玻璃':
            spec.multi_layer_acoustic_glass = value
        elif prop == '外后视镜功能':
            spec.exterior_mirror_function = value
        elif prop == '内后视镜功能':
            spec.interior_mirror_function = value
        elif prop == '后风挡遮阳帘':
            spec.rear_windshield_sunshade = value
        elif prop == '后排侧窗遮阳帘':
            spec.rear_side_window_sunshade = value
        elif prop == '后排侧隐私玻璃':
            spec.rear_side_privacy_glass = value
        elif prop == '车内化妆镜':
            spec.interior_mirror = value
        elif prop == '后雨刷':
            spec.rear_wiper = value
        elif prop == '感应雨刷功能':
            spec.induction_wiper_function = value
        else:
            self.un_parse_props.append(prop)

    def parse_temperature(self, prop, value):
        """
        :type prop: str
        :type value: str
        """
        ignore_props = self.ignore_props.get(
            self.group, self.default_ignore_props)
        spec = self.spec
        if prop in ignore_props:
            pass
        elif prop == '空调温度控制方式':
            spec.air_conditioning_temperature_control_method = value
        elif prop == '后排独立空调':
            spec.rear_independent_air_conditioner = value
        elif prop == '后座出风口':
            spec.rear_seat_outlet = value
        elif prop == '温度分区控制':
            spec.temperature_zone_control = value
        elif prop == '车载空气净化器':
            spec.air_purifier = value
        elif prop == '车载冰箱':
            spec.refrigerator = value
        elif prop == '车内PM2.5过滤装置':
            spec.pm25_filter_unit = value
        elif prop == '负离子发生器':
            spec.negative_ion_generator = value
        elif prop == '车内香氛装置':
            spec.interior_fragrance_device = value
        else:
            self.un_parse_props.append(prop)

    def parse_motor(self, prop, value):
        """
        :type prop: str
        :type value: str
        """
        ignore_props = self.ignore_props.get(
            self.group, self.default_ignore_props)
        spec = self.spec
        if prop in ignore_props:
            pass
        elif prop in ['工信部纯电续航里程(km)', '工信部续航里程(km)']:
            spec.official_range = value
        elif prop == '电动机总功率(kW)':
            spec.motor_total_power = value
        elif prop == '电动机总扭矩(N·m)':
            spec.motor_total_torque = value
        elif prop == '前电动机最大功率(kW)':
            spec.motor_front_max_power = value
        elif prop == '前电动机最大扭矩(N·m)':
            spec.motor_front_max_torque = value
        elif prop == '后电动机最大功率(kW)':
            spec.motor_rear_max_power = value
        elif prop == '后电动机最大扭矩(N·m)':
            spec.motor_rear_max_torque = value
        elif prop == '系统综合功率(kW)':
            spec.motor_comprehensive_power = value
        elif prop == '系统综合扭矩(N·m)':
            spec.motor_comprehensive_torque = value
        elif prop == '驱动电机数':
            spec.motors = value
        elif prop == '电机布局':
            spec.motor_layout = value
        elif prop == '电池类型':
            spec.battery_type = value
        elif prop in ['电池容量(kWh)', '电池能量(kWh)']:
            spec.battery_capacity = value
        elif prop == '百公里耗电量(kWh/100km)':
            spec.power_consumption = value
        elif prop == '电池组质保':
            spec.battery_pack_warranty = value
        elif prop == '电池充电时间':
            spec.battery_charging_time = value
        elif prop == '快充电量(%)':
            spec.fast_charge = value
        elif prop == '快充时间(小时)':
            spec.fast_charging_time = value
        elif prop == '慢充时间(小时)':
            spec.slow_charging_time = value
        else:
            self.un_parse_props.append(prop)
