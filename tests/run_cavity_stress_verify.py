import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.nodes.cavity_resonator import CavityResonatorNode
from src.nodes.boundary_stress_integrator import BoundaryStressIntegratorNode

print('=== Starting Verification ===')
cavity = CavityResonatorNode()
stress_node = BoundaryStressIntegratorNode()

state = cavity.process({'omega_bare': 1.0e14, 'plasma_frequency': 2.0e13, 'coupling_J': 5.0e10, 'damping_kappa': 1.0e8, 'intracavity_photons': 1.0e12, 'cavity_length': 0.05, 'beam_cross_section': 1.0e-4})
print('Screened Frequency:', state.get('omega_screened'))
print('Supermodes (+/-):', state.get('omega_plus'), state.get('omega_minus'))

out = stress_node.process(state)
print('Pressure Left/Right:', out.get('pressure_left'), out.get('pressure_right'))
print('T_00 / T_zz:', out.get('T_00'), out.get('T_zz'))
print('Net Thrust:', out.get('net_thrust'))
print('=== Done ===')
