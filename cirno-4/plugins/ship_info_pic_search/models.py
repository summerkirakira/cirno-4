from pydantic import BaseModel, validator
from typing import Optional, Union, Tuple
from thefuzz import process
import pathlib
import json

from nonebot import require

require("nonebot_plugin_localstore")


import nonebot_plugin_localstore as store

image_path = store.get_data_dir("ship_info_pic_search")
ship_info_path = image_path / "ship_group.json"
current_path = pathlib.Path(__file__).parent

if not ship_info_path.exists():
    with (current_path / "ship_group.json").open("r", encoding="utf-8") as f:
        ship_info_path.write_text(f.read(), encoding="utf-8")

class ManufacturerData(BaseModel):

    class Data(BaseModel):
        calculatorName: Optional[str] = None
        name: str
        chineseName: Optional[str] = None
        nameSmall: str
        ref: str

    calculatorType: str = "manufacturer"
    data: Data


class ComponentData(BaseModel):

    class Data(BaseModel):
        manufacturerData: Optional[ManufacturerData] = None
        description: Optional[str] = None
        grade: str
        itemClass: Optional[str] = None
        health: int = 0
        mass: int = 0
        name: str = "-"
        chineseName: Optional[str] = None
        chineseNameShort: Optional[str] = None
        chineseDescription: Optional[str] = None
        shortName: Optional[str] = None
        ref: str
        size: int = 0
        subType: Optional[str] = None
        type: str
        chineseTypeName: str = "未知"

    class Damage(BaseModel):
        damagePhysical: float = 0
        damageBiochemical: float = 0
        damageDistortion: float = 0
        damageEnergy: float = 0
        damageStun: float = 0
        damageThermal: float = 0

    class Distortion(BaseModel):
        decayDelay: float
        decayRate: float
        maximum: float
        powerChangeOnlyAtMaxDistortion: bool
        powerRatioAtMaxDistortion: bool
        recoveryRatio: float
        warningRatio: float

    class Heat(BaseModel):
        mass: float
        maxCoolingRate: float
        temperatureToIR: float

    class Power(BaseModel):
        decayRateOfEM: float
        isOverclockable: bool
        isThrottleable: bool
        overclockPerformance: float
        overclockThresholdMax: float
        overclockThresholdMin: float
        overpowerPerformance: float
        powerBase: float
        powerDraw: float
        timeToReachDrawRequest: float
        powerToEM: float

    localName: str
    data: Data
    type: str = "-"

    @validator('localName')
    def local_name_no_scitem(cls, v):
        v = v.replace("_scitem", "")
        return v

    def get_match_ratio(self, name: str) -> float:
        name_list: list[str] = []
        if self.localName:
            name_list.append(self.localName)
        if self.data.name:
            name_list.append(self.data.name)
        if self.data.chineseName:
            name_list.append(self.data.chineseName)
        if self.data.shortName:
            name_list.append(self.data.shortName)
        result: Optional[tuple[str, float]] = process.extractOne(name, name_list)
        if result:
            return result[1]
        return 0.0


class MissileData(BaseModel):
    damage: ComponentData.Damage
    linearSpeed: int = 0
    lockRangeMax: int = 0
    lockRangeMin: int = 0
    lockTime: float = 0
    lockingAngle: int = 0
    trackingSignalType: str
    lockSignalAmplifier: float = 0
    hitType: str
    fuelTankSize: float = 0
    explosionSafetyDistance: float = 0


class BombData(BaseModel):
    armTime: float = 0
    damage: ComponentData.Damage
    explosionSafetyDistance: float = 0
    maxLifetime: float = 0


class ShieldData(BaseModel):
    damagedRegenDelay: float = 0
    decayRatio: float = 0
    downedRegenDelay: float = 0
    maxShieldHealth: float = 0
    maxShieldRegen: float = 0
    regenExcessChargePerSec: float = 0
    regenExcessMax: float = 0
    regenExcessUseCooldown: float = 0


class WeaponData(BaseModel):

    class FireActions(BaseModel):
        ammoCost: int = 0
        damageMultiplier: float = 0
        delay: float = 0
        fireRate: float = 0
        heatPerShot: float = 0
        pelletCount: int = 0

    class Spread(BaseModel):
        attack: float = 0
        decay: float = 0
        firstAttack: float = 0
        max: float = 0
        min: float = 0

    class Damage(BaseModel):
        alphaMax: float = 0
        alphaMin: float = 0
        fireRateMax: float = 0
        fireRateMin: float = 0

    class Regen(BaseModel):
        requestedRegenPerSec: float = 0
        regenerationCooldown: float = 0
        regenerationCostPerBullet: float = 0
        requestedAmmoLoad: int = 0

    idealCombatRange: float = 0
    fireActions: FireActions
    damage: Damage
    spread: Spread
    regen: Optional[Regen] = None


class CoolerData(BaseModel):
    coolingRate: float = 0
    suppressionHeatFactor: float = 0
    suppressionIRFactor: float = 0


class EMPData(BaseModel):
    chargeTime: float = 0
    cooldownTime: float = 0
    distortionDamage: float = 0
    empRadius: float = 0
    minEmpRadius: float = 0
    minPhysRadius: float = 0
    physRadius: float = 0
    pressure: float = 0
    unleashTime: float = 0


class MiningLaserData(BaseModel):
    catastrophicChargeWindowRateModifier: float = 0
    laserInstability: float = 0
    optimalChargeWindowRateModifier: float = 0
    optimalChargeWindowSizeModifier: float = 0
    resistanceModifier: float = 0
    shatterdamageModifier: float = 0
    throttleLerpSpeed: float = 0


class PortData(BaseModel):
    maxSize: int = 0
    minSize: int = 0

    class ItemType(BaseModel):
        subType: Optional[str]
        type: Optional[str]

    itemTypes: Optional[list[ItemType]] = None


class QDriveData(BaseModel):
    disconnectRange: float = 0

    class HeatParams(BaseModel):
        inFlightThermalEnergyDraw: float = 0
        postRampDownThermalEnergyDraw: float = 0
        preRampUpThermalEnergyDraw: float = 0
        rampDownThermalEnergyDraw: float = 0
        rampUpThermalEnergyDraw: float = 0

    class Params(BaseModel):
        calibrationDelayInSeconds: float = 0
        calibrationProcessAngleLimit: float = 0
        calibrationRate: float = 0
        calibrationWarningAngleLimit: float = 0
        cooldownTime: float = 0
        driveSpeed: float = 0
        engageSpeed: float = 0
        interdictionEffectTime: float = 0
        maxCalibrationRequirement: float = 0
        minCalibrationRequirement: float = 0
        spoolUpTime: float = 0
        stageOneAccelRate: float = 0
        stageTwoAccelRate: float = 0

    heatParams: HeatParams
    params: Params
    jumpRange: float = 0
    quantumFuelRequirement: float = 0


class MissileRackData(BaseModel):
    detachVelocityForward: float = 0
    detachVelocityRight: float = 0
    detachVelocityUp: float = 0
    igniteOnPylon: bool = False
    launchDelay: float = 0
    localName: str = ""


class Missile(ComponentData):
    type: str = "missile"

    class Data(ComponentData.Data):
        subType: str = "Missile"
        type: str = "Missile"
        missile: MissileData
        chineseTypeName = "导弹"

    def get_damage(self) -> float:
        return self.data.missile.damage.damageEnergy + self.data.missile.damage.damagePhysical + self.data.missile.damage.damageThermal + self.data.missile.damage.damageBiochemical + self.data.missile.damage.damageBiochemical

    data: Data
    localName: str


class Bomb(ComponentData):
    type: str = "Bomb"

    class Data(ComponentData.Data):
        subType: str = "Bomb"
        type: str = "Bomb"
        bomb: BombData
        chineseTypeName = "炸弹"

    data: Data


class Shield(ComponentData):
    type: str = "Shield"

    class Data(ComponentData.Data):
        subType: str = "Shield"
        type: str = "Shield"
        shield: ShieldData
        distortion: ComponentData.Distortion
        heat: ComponentData.Heat
        power: ComponentData.Power
        chineseTypeName = "护盾"

    data: Data


class Weapon(ComponentData):
    type: str = "Weapon"

    class Data(ComponentData.Data):
        class AmmoContainer(BaseModel):
            initialAmmoCount: int = 0
            maxAmmoCount: int = 0
            ammoRef: str

        class Ammo(BaseModel):
            calculatorType: str

            class Data(BaseModel):
                ref: str

                class Damage(BaseModel):
                    damagePhysical: float = 0
                    damageEnergy: float = 0
                    damageDistortion: float = 0
                    damageThermal: float = 0
                    damageBiochemical: float = 0
                    damageStun: float = 0

                damage: Damage
                size: int = 0
                lifetime: float = 0
                speed: float = 0
            data: Data
            localName: str

        subType: str = "Gun"
        type: str = "WeaponGun"
        chineseTypeName = "武器"
        weapon: WeaponData
        distortion: ComponentData.Distortion
        heat: ComponentData.Heat
        power: ComponentData.Power
        ammoContainer: AmmoContainer
        ammo: Ammo
        group: str = ""

    data: Data


class Cooler(ComponentData):
    type: str = "Cooler"

    class Data(ComponentData.Data):
        subType: str = "Cooler"
        type: str = "Cooler"
        cooler: CoolerData
        # distortion: ComponentData.Distortion
        heat: ComponentData.Heat
        power: ComponentData.Power
        itemClass: Optional[str] = None
        chineseTypeName = "冷却器"

    data: Data


class EMP(ComponentData):
    type: str = "EMP"

    class Data(ComponentData.Data):
        subType: str = "EMP"
        type: str = "EMP"
        emp: EMPData
        distortion: ComponentData.Distortion
        heat: ComponentData.Heat
        power: ComponentData.Power
        chineseTypeName = "EMP"

    data: Data


class MiningLaser(ComponentData):
    type: str = "MiningLaser"

    class Data(ComponentData.Data):
        subType: str = "Gun"
        type: str = "WeaponMining"
        miningLaser: MiningLaserData
        heat: ComponentData.Heat
        power: ComponentData.Power
        chineseTypeName = "采矿激光"

        class Weapon(BaseModel):
            idealCombatRange: float = 0
            supplementaryFireTime: float = 0

            class Mining(BaseModel):
                energyRate: float = 0
                fullDamageRange: float = 0
                heatPerSecond: float = 0
                hitRadius: float = 0
                zeroDamageRange: float = 0
                damage: ComponentData.Damage

            mining: Mining

        weapon: Weapon

    data: Data


class Mount(ComponentData):
    type: str = "Mount"
    subType: str = "Mount"

    class Data(ComponentData.Data):
        ports: Optional[list[PortData]] = None
        heat: ComponentData.Heat
        power: ComponentData.Power
        chineseTypeName = "挂载点"

    data: Data

    localName: str = ""


class PowerPlant(ComponentData):
    type: str = "PowerPlant"
    subType: str = "PowerPlant"

    class Data(ComponentData.Data):
        heat: ComponentData.Heat
        power: ComponentData.Power
        distortion: ComponentData.Distortion
        chineseTypeName = "发电机"

    data: Data


class QDrive(ComponentData):
    type: str = "QDrive"
    subType: str = "QDrive"

    class Data(ComponentData.Data):
        heat: ComponentData.Heat
        power: ComponentData.Power
        distortion: ComponentData.Distortion
        qdrive: QDriveData
        chineseTypeName = "量子引擎"

    data: Data

    def get_velocity_in_light(self):
        return round(self.data.qdrive.params.driveSpeed / (3 * 10**8), 2)


class Qed(ComponentData):
    type: str = "QED"
    subType: str = "QED"

    class Data(ComponentData.Data):
        heat: ComponentData.Heat
        power: ComponentData.Power

        class Interdiction(BaseModel):
            activationPhaseDurationSeconds: float = 0
            activePowerDrawFraction: float = 0
            chargeTimeSecs: float = 0
            cooldownTimeSecs: float = 0
            decreaseChargeRateTimeSeconds: float = 0
            dischargeTimeSecs: float = 0
            disperseChargeTimeSeconds: float = 0
            greenZoneCheckRange: float = 0
            increaseChargeRateTimeSeconds: float = 0
            maxChargeRatePowerDrawFraction: float = 0
            maxPowerDraw: float = 0
            radiusMeters: float = 0
            stopChargingPowerDrawFraction: float = 0
            tetheringPowerDrawFraction: float = 0

        class Jammer(BaseModel):
            greenZoneCheckRange: float = 0
            jammerRange: float = 0
            maxPowerDraw: float = 0

        interdiction: Interdiction
        jammer: Jammer
        chineseTypeName = "量子干扰器"

    data: Data


class Utility(ComponentData):
    type: str = "Utility"
    subType: str = "Utility"

    class Data(ComponentData.Data):

        class Modifier(BaseModel):
            canInterrupt: bool = False
            isInterruptible: bool = False
            charges: int = 0

            class MiningModifier(BaseModel):
                catastrophicChargeWindowRateModifier: float = 0
                laserInstability: float = 0
                optimalChargeWindowRateModifier: float = 0
                optimalChargeWindowSizeModifier: float = 0
                resistanceModifier: float = 0
                shatterdamageModifier: float = 0

            class WeaponModifier(BaseModel):
                extractorDamageMultiplier: float = 0
                laserDamageMultiplier: float = 0

            miningModifier: Optional[MiningModifier]
            weaponModifier: Optional[WeaponModifier]

        modifier: Optional[Modifier]
        requiredTags: str = ""
        chineseTypeName = "工具"
    data: Data


class MissileRack(ComponentData):
    type: str = "MissileRack"
    subType: str = "MissileRack"

    class Data(ComponentData.Data):
        heat: Optional[ComponentData.Heat]
        power: Optional[ComponentData.Power]
        missileRack: Optional[MissileRackData]
        ports: Optional[list[PortData]] = None
        chineseTypeName = "导弹架"

    data: Data


class Paint(BaseModel):
    type: str = "Paint"
    subType: str = "Paint"

    class Data(BaseModel):
        grade: str
        manufacturerRef: Optional[str] = None
        chineseNameShort: Optional[str] = None
        chineseName: Optional[str] = None
        chineseDescription: Optional[str] = None
        manufacturerData: Optional[ManufacturerData] = None
        ref: str
        requiredTags: Optional[str] = None
        size: int
        type: str
        chineseTypeName = "涂装"

    data: Data
    calculatorType: str
    localName: str


class Shop(BaseModel):

    calculatorType: str = "shop"

    class Data(BaseModel):
        location: str
        locationChinese: Optional[str] = None
        name: str
        nameChinese: Optional[str] = None

        class Item(BaseModel):
            basePrice: int
            localName: str
            price: int
            ref: str
            item: Optional[ComponentData] = None

        inventory: list[Item]
        chineseTypeName = "商店"
    data: Data

    def get_match_ratio(self, name: str) -> float:
        name_list: list[str] = [f"{self.data.locationChinese} {self.data.nameChinese}"]
        name_list.append(f"{self.data.location} {self.data.name}")
        result: Optional[tuple[str, float]] = process.extractOne(name, name_list)
        if result:
            return result[1]
        return 0.0


class SearchItem(BaseModel):

    calculatorType: str = "search"

    class Result(BaseModel):
        shop: Shop
        item: Shop.Data.Item

    results: list[Result] = []


class Ship(ComponentData):

    class Data(ComponentData.Data):

        class Loadout(BaseModel):
            itemPortName: str
            localName: str
            minSize: Optional[int]
            maxSize: Optional[int]

            class ItemType(BaseModel):
                type: str

            class SubLoadout(BaseModel):
                itemPortName: str
                localName: str
                component: Union[ComponentData, Missile, None]

            itemTypes: Optional[list[ItemType]]
            requiredTags: Optional[str] = None
            portTags: Optional[str] = None
            loadout: Optional[list[SubLoadout]] = None
            mount: Union[Mount, MissileRack, None] = None

        class Ifcs(BaseModel):

            class AngularVelocity(BaseModel):
                x: float
                y: float
                z: float

            class Afterburner(BaseModel):
                class AfterburnAccelMultiplier(BaseModel):
                    x: float
                    y: float
                    z: float

                class AfterburnAngAccelMultiplier(BaseModel):
                    x: float
                    y: float
                    z: float

                capacitorMax: float
                capacitorAfterburnerIdleCost: float
                capacitorRegenPerSec: float
                afterburnAccelMultiplier: AfterburnAccelMultiplier
                afterburnAngAccelMultiplier: AfterburnAngAccelMultiplier

            maxSpeed: float
            maxAfterburnSpeed: float
            angularVelocity: AngularVelocity
            afterburner: Afterburner

        class Items(BaseModel):
            class Cargo(BaseModel):
                class Data(BaseModel):
                    class CargoGrid(BaseModel):
                        class Inventory(BaseModel):
                            class Data(BaseModel):
                                class MaxPermittedItemSize(BaseModel):
                                    x: float
                                    y: float
                                    z: float

                                maxPermittedItemSize: Optional[MaxPermittedItemSize]

                                class InteriorDimensions(BaseModel):
                                    x: float
                                    y: float
                                    z: float
                                interiorDimensions: InteriorDimensions

                            data: Data

                        inventory: Optional[Inventory]

                    cargoGrid: Optional[CargoGrid]
                    type: str
                data: Data
            cargos: list[Cargo]

            def get_inventory_size(self) -> float:
                size: float = 0.0
                for cargo in self.cargos:
                    if cargo.data.cargoGrid:
                        if cargo.data.type == "Cargo":
                            size += cargo.data.cargoGrid.inventory.data.interiorDimensions.x * \
                                    cargo.data.cargoGrid.inventory.data.interiorDimensions.y * \
                                    cargo.data.cargoGrid.inventory.data.interiorDimensions.z

                return size

        loadout: list[Loadout]
        ifcs: Optional[Ifcs] = None
        items: Items

        components: Optional[list[ComponentData]] = None

        class Vehicle(BaseModel):
            vehicleDefinition: str
            modification: str
            dogfightEnabled: bool
            crewSize: int
            career: str
            role: str

            class Size(BaseModel):
                x: float
                y: float
                z: float

            size: Size
            inventory: str

        vehicle: Vehicle

        class Hull(BaseModel):
            mass: float

            class Hp(BaseModel):
                name: str
                hp: float

            hp: list[Hp]
            maxAngularVelocity: Optional[list[float]]
            maxAngularAcceleration: Optional[list[float]]

        hull: Hull

        class Shield(BaseModel):
            faceType: str
            shieldManagementAllowed: bool
            MaxReallocation: float
            minDamageStrengthRange: float
            maxDamageStrengthRange: float
            maxHitImpact: float

        shield: Optional[Shield]

        class Armor(BaseModel):
            class Data(BaseModel):
                type: str
                ref: str

                class ArmorData(BaseModel):
                    class DamageMultiplier(BaseModel):
                        damagePhysical: float
                        damageEnergy: float
                        damageDistortion: float
                        damageThermal: float
                        damageBiochemical: float

                    damageMultiplier: DamageMultiplier
                armor: ArmorData
            data: Data

        armor: Optional[Armor]

        class WeaponRegenPoolCrew(BaseModel):
            regenFillRate: float
            ammoLoad: float
            respectsCapacitorAssignments: bool

        weaponRegenPoolCrew: Optional[WeaponRegenPoolCrew]

        class WeaponRegenPoolTurret(BaseModel):
            regenFillRate: float
            ammoLoad: float
            respectsCapacitorAssignments: bool

        weaponRegenPoolTurret: Optional[WeaponRegenPoolTurret]

        chineseTypeName = "舰船"

        cargo: float
        fuelCapacity: float
        qtFuelCapacity: float

    class Sku(BaseModel):
        name: str
        price: int

    data: Data
    isFlyable: bool = False
    loanerShips: list[str] = []
    # alias = list[str]
    # cirno_id: int
    # skus: list[Sku] = []


class ShopSearch(BaseModel):
    Item: ComponentData
    shops: list[Shop]


class Sheet(BaseModel):

    class Column(BaseModel):
        data: list[str]

    columns: list[Column]
    title: str
    width: int = 1000
    width_ratio: list[float]
    column_size: int
    margin: int = 20
    row_height: int = 50
    header_height: int = 80
    colors: list[str] = ["#f2f2f3", "#ffffff"]


class ShipNameBinding(BaseModel):
    local_name: str
    ship_name: str
    photo_name: str
    upgrade_name: str
    ship_price: int


class Archive(BaseModel):
    ships: list[Ship]
    weapons: list[Weapon]
    missiles: list[Missile]
    shops: list[Shop]
    bombs: list[Bomb]
    shields: list[Shield]
    coolers: list[Cooler]
    emps: list[EMP]
    mining_lasers: list[MiningLaser]
    mounts: list[Mount]
    power_plants: list[PowerPlant]
    quantum_drives: list[QDrive]
    qeds: list[Qed]
    utilities: list[Utility]
    paints: list[Paint]
    missile_racks: list[MissileRack]


class ShipGroup(BaseModel):
    class ShipInfo(BaseModel):
        manufacturer: str
        series: Optional[str]
        local_name: str
        name: str
        description: Optional[str]
        upgrade_name: str
        alias: list[str]
        manufacturer: str
        price: Optional[int] = None
        chinese_name: str
        photo_name: str
        alias: list[str] = []
        ship: Ship

    ships: list[ShipInfo] = []

    def save_all(self):
        with open(ship_info_path.absolute(), "w", encoding="utf-8") as f:
            f.write(self.json(indent=4, ensure_ascii=False))

    def load_all(self):
        with open(ship_info_path.absolute(), "r", encoding="utf-8") as f:
            data = json.load(f)
            self.ships = [ShipGroup.ShipInfo(**d) for d in data["ships"]]

    @staticmethod
    def get_binding_by_local_name(local_name: str) -> Optional[ShipNameBinding]:
        ship_name_binding_path = pathlib.Path(__file__).parent / "ship_name_binding.json"

        with open(ship_name_binding_path, 'r') as f:
            data = json.load(f)
            ship_name_binding = [ShipNameBinding(**d) for d in data]

        for binding in ship_name_binding:
            if binding.local_name == local_name:
                return binding
        return None

    def add_ship(self, ship: Ship):
        upgrade_binding = self.get_binding_by_local_name(ship.localName)
        self.ships.append(
            ShipGroup.ShipInfo(
                local_name=ship.localName,
                name=ship.data.name,
                description=ship.data.chineseDescription,
                upgrade_name=upgrade_binding.upgrade_name,
                alias=[],
                manufacturer=ship.data.manufacturerData.data.name,
                price=upgrade_binding.ship_price,
                chinese_name=ship.data.chineseName,
                series=None,
                ship=ship,
                photo_name=upgrade_binding.photo_name
            )
        )

    def add_ships(self, ships: list[Ship]):
        for ship in ships:
            self.add_ship(ship)

    def add_series(self):
        for ship in self.ships:
            if ship.series is None:
                series_name = input(f"请输入{ship.chinese_name}({ship.name})的系列名, 无则留空: ")
                if series_name == "":
                    ship.series = ship.name
                else:
                    ship.series = series_name
                self.save_all()

    def add_aliases(self):
        with open("alias.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        for ship_name in data:
            is_find = False
            for ship in self.ships:
                if ship.name in ship_name:
                    user_input = input(f"即将为{ship.chinese_name}({ship.name})添加别名{ship_name}, 确认请输入y: ")
                    if user_input == "y":
                        ship.alias += data[ship_name]
                        self.save_all()
                        is_find = True
                        break
            if not is_find:
                print(f"未找到{ship_name}")
                user_input = input("请输入该舰船的localName: ")
                for ship in self.ships:
                    if ship.ship.localName == user_input:
                        ship.alias += data[ship_name]
                        self.save_all()
                        break

    def add_alias(self, local_name: str, alias: str):
        for ship in self.ships:
            if ship.local_name == local_name:
                if alias not in ship.alias:
                    ship.alias.append(alias)
                    self.save_all()
                    break

    def get_ship_by_name(self, name: str) -> Optional[ShipInfo]:
        name = name.lower()
        for ship in self.ships:
            if ship.name == name:
                return ship
            if ship.chinese_name == name:
                return ship
            for alias in ship.alias:
                if alias == name:
                    return ship
        return None

    def get_ships_by_manufacturer(self, manufacturer: str) -> list[ShipInfo]:
        return [ship for ship in self.ships if ship.manufacturer == manufacturer or ship.ship.data.manufacturerData.data.chineseName == manufacturer]

    def get_ships_by_series(self, series: str) -> list[ShipInfo]:
        return [ship for ship in self.ships if ship.series == series]

    def get_manufacturer_names(self) -> list[Tuple[str, str]]:
        manufacturer_dict = {}
        for ship in self.ships:
            manufacturer_dict[ship.ship.data.manufacturerData.data.chineseName] = ship.manufacturer
        return list(manufacturer_dict.items())

    def get_series_names(self) -> list[str]:
        series_dict = {}
        for ship in self.ships:
            series_dict[ship.series] = ship.series
        return list(series_dict.keys())
