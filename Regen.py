import random
import numpy as np
import matplotlib.pyplot as plt
import json
from rocketcea.cea_obj_w_units import CEA_Obj
import rocketprops.rocket_prop as prop

def final(df):
    """ Use this function to actually start the simulation,
    once it is started you can just use this to store the results from
    it inside of df to then send back to main python script"""
    df = df.copy()  # to avoid modifying original df if you want

    # This is used to obtain new columns in the output excel file
    df["Area"] = np.pi * df["r"] ** 2
    df["Temperature"] = [random.randint(1, 100) for _ in range(len(df))]
    return df


class sim():
    def __init__(self, df):
        """Starting here we save the data from the IC.json file
        Data saves: T_0, P_0, m_dot"""
        # This will load the information from the IC.json file
        IC = "IC.json"
        with open(IC, 'r') as file:
            IC = json.load(file)

        self.pc = float(IC['pc'])  # Pressure in MPa or whatever unit
        self.mr = float(IC['mr'])  # Mixture ratio
        self.mdot = float(IC['mdot'])  # Mass flow rate
        self.channel_count = float(IC['R_number']) # Number of channels
        self.oxidizer = IC['ox']
        self.fuel = IC['fuel']

        self.ceaobject = CEA_Obj(
            oxName               = self.oxidizer, # LOX
            fuelName             = self.fuel, # RP1           
            isp_units            = 'sec',
            cstar_units          = 'm/s',
            pressure_units       = 'bar', # Pressure output is bar, not Pa! SI units for pressure is Pa
            temperature_units    = 'K',
            sonic_velocity_units = 'm/s',
            enthalpy_units       = 'J/kg',
            density_units        = 'kg/m^3',
            specific_heat_units  = 'J/kg-K',
            viscosity_units      = 'poise' # Viscosity output is poise, not Pa-s! SI units for dynamic viscosity are Pa-s.
        )

        # Chamber Geometry
        self.x=df['x']
        self.radius=df['r']
        self.radius_throat           = min(df['r']) # [m] - Radius of the throat
        self.diameter                = 2 * self.radius # [m] - Diameter as a function of x
        self.diameter_throat         = 2 * self.radius_throat # [m] - Diameter of the throat
        self.area                    = np.pi * np.square(self.radius) # [m^2] - Chamber cross sectional area as function of x
        self.area_throat             = min(self.area) # [m^2] - Area of throat
        self.area_ratio              = self.area / self.area_throat # [dimensionless] - Chamber area / throat area
        self.throat_index            = np.where(self.radius == min(self.radius))[0][0] # [dimensionless] - Index of throat
        self.radius_curvature_throat = 0.382 * self.radius_throat # [m] This is based on a Rao Nozzle
        self.thickness_wall          = 0.75/1000.0 # [m] = 0.75 mm - Based on minimum printable wall thickness
        # self.thickness_fin           = thickness_fin # [m] Fin thickness between cooling channels

        # Engine Performance
        # self.pc         = Pc # [barA] - Chamber total (stagnation) pressure
        # self.mr         = mr # [dimensionless] - Mixture ratio (mdot_ox / mdot_fuel)
        self.cstar      = self.ceaobject.get_Cstar(Pc=self.pc, MR=self.mr) # [m/s] - Characteristic velocity
        # self.mdot = mdot # [kg/s] - Total engine mass flow rate
        self.mdot_fuel  = self.mdot / (1 + self.mr) # [kg/s] - Fuel mass flow rate

        # Combustion Gas Properties
        self.total_temperature        = self.ceaobject.get_Tcomb(Pc=self.pc, MR=self.mr) # [K] - Chamber total (stagnation) temperature (i.e. flame temperature)
        transport_properties          = self.ceaobject.get_Chamber_Transport(Pc=self.pc, MR=self.mr, eps=1, frozen=1) # (specifc heat, viscostiy, thermal conductivity, Prandtl Number)
        self.specific_heat_gas        = transport_properties[0] # [J/(kg*K)] - Combustion gas specific heat at constant pressure
        self.viscosity_gas            = transport_properties[1] * 0.1 # [Pa*s] - Combustion gas viscosity (0.1 factor to convert Poise to Pa*s)
        self.thermal_conductivity_gas = transport_properties[2] # [W/(m*K)] - Combustion gas thermal conductivity
        self.prandtl_gas              = transport_properties[3] # [dimensionless] - Combustion gas Prandtl number
        self.mach                     = self.set_Mach() # [dimensionless] Mach number as a function of x
        self.gamma_gas                = self.set_gammaGas() # [dimensionless] - Ratio of specific heats (Cp/Cv) as a function of x

        # Heat Transfer
        self.adiabatic_wall_temp       = self.set_adiabaticWallTemp() # [K] - Adibatic wall temperature as a function of x
        self.wall_temperature_gas      = np.ones(len(self.x)) * 500.0 # [K] - Gas-side wall temperature as function of x. NOTE: intial guess
        self.wall_temperature_coolant  = np.ones(len(self.x)) * 500.0 # [K] - Coolant-side wall temperature as a function of x. NOTE: initial guess
        self.h_Bartz                   = self.get_h_Bartz() # [W/(m^2*K)] - Gas-side heat transfer coefficient
        self.heat_flux                 = self.set_heatFlux() # [W/m^2] - Heat flux as function of x
        self.thermal_conductivity_wall = 11.4 # [W/(m*K)] TODO: refine for inco 718
        self.resistance_soot           = self.set_sootResistance() # [m^2*K/W] - Soot thermal resistance

        # Channel Geometry
        self.width_channel              = width_channel # [m] - Cooling channel width (parallel with chamber circumfrence)
        self.height_channel             = height_channel # [m] - Cooling channel height (perpendicular with chamber circumfrence)
        self.aspect_ratio               = self.height_channel / self.width_channel
        self.area_channel               = width_channel * height_channel # [m^2] - Cooling channel cross-sectional area
        self.hydraulic_diameter_channel = 4 * self.area_channel / (2 * (self.width_channel + self.height_channel)) # [m] - Cooling channel hydraulic diameter
        self.channel_count              = 67 # Number of cooling channels TODO: make this an input
        self.surface_roughness = 15e-6 # [m] - Surface Roughness

        # Channel Transport Properties
        self.mdot_channel                 = self.mdot_fuel / self.channel_count # [kg/s] - Fuel mass flow rate through one channel
        self.temperature_coolant          = self.get_coolantTemp(300) # [K] - Coolant bulk temperature as a function of x TODO: refine coolant inlet temperature
        self.density_coolant              = self.get_prop_RP1('rho', self.temperature_coolant) # [kg/m^3] - Coolant bulk density
        self.specific_heat_coolant        = self.get_prop_RP1('cp', self.temperature_coolant) # [J/(kg*K)] - Coolant bulk specific heat
        self.viscosity_coolant            = self.get_prop_RP1('mu', self.temperature_coolant) # [Pa*s] - Coolant bulk viscosity
        self.thermal_conductivity_coolant = self.get_prop_RP1('k', self.temperature_coolant) # [W/(m*K)] - Coolant bulk thermal conductivity
        self.velocity_coolant             = self.get_coolantVelocity() # [m/s] - Coolant velocity
        self.reynolds_coolant             = self.get_coolantReynolds() # [dimensionless] - Coolant Reynold's number
        self.friction_factor              = self.get_channelFrictionFactor() # Darcy-Weisbach friction factor of coolant
        self.prandtl_coolant              = self.get_coolantPradntl() # [dimensionless] - Coolant Prandtl number
        self.nusselt_coolant              = self.get_coolantNusselt() # [dimensionless] - Coolant Nusselt number
        self.h_coolant                    = self.get_h_coolant() # [W/(m^2*K)] - Coolant convective heat transfer coefficient
        self.pressure_coolant             = self.get_coolantPressure(inlet_total_pressure=31) # [barA] - Coolant static pressure
        self.pressure_drop_coolant        = 0
        self.fin_effectiveness            = self.get_finEffectiveness() # [dimensionless] - Cooling channel fin efficiency

    def get_q_gas_side(self):
        # q = h_g*(T_aw-T_wg)
        # q heat flux
        # h_g Gas side heat transfer coefficient 
        # T_aw adiabatic wall temperature
        # T_wg Temperature wall gas

        # q=h_g*(T_aw-T_wg)
        return 1

    def get_hg(self):
        # h_g = [(0.026/Dt^0.2)*(mu^0.2 *Cp/Pr^0.6)_ns ((pc)_ns *g/c*)^0.8 (Dt/R)^0.1]*(At/A)^0.9 *sigma
        # hg = Gas side heat tranfer
        # R Radius of curvature
        # sigma Correction factor for property variations across the boundary layer 
        # A Area under consideration
        return 1
    
    def get_sigma(self):
        # sigma = 1/[((1/2)*T_wg/Tc_ns*0.5*(1+(g-1)*M^2)+0.5)^0.68 * (1+0.5*(1+(g-1)*M^2))^0.12]
        return 1

# import os
# import pandas as pd
# input_file="example.csv"
# input_dir = os.path.dirname(os.path.abspath(input_file))
# #Obtain the dataframe to start with
# df = pd.read_csv(input_file)

# Hey=sim(df)