/*
 *  aeif_cond_exp_custom.cpp
 *
 *  This file is part of NEST
 *
 *  Copyright (C) 2010 by
 *  The NEST Initiative
 *
 *  See the file AUTHORS for details.
 *
 *  Permission is granted to compile and modify
 *  this file for non-commercial use.
 *  See the file LICENSE for details.
 *
 */

#include "aeif_cond_exp_custom.h"
#include "nest_names.h"

#ifdef HAVE_GSL_1_11

#include "universal_data_logger_impl.h"

#include "exceptions.h"
#include "network.h"
#include "dict.h"
#include "integerdatum.h"
#include "doubledatum.h"
#include "dictutils.h"
#include "numerics.h"
#include <limits>

#include <gsl/gsl_errno.h>

#include <cmath>
#include <iomanip>
#include <iostream>
#include <cstdio>

/* ---------------------------------------------------------------- 
 * Recordables map
 * ---------------------------------------------------------------- */

nest::RecordablesMap<nest::aeif_cond_exp_custom> nest::aeif_cond_exp_custom::recordablesMap_;

namespace nest
{

  /*
   * template specialization must be placed in namespace
   *
   * Override the create() method with one call to RecordablesMap::insert_() 
   * for each quantity to be recorded.
   */
  template <>
  void RecordablesMap<aeif_cond_exp_custom>::create()
  {
    // use standard names whereever you can for consistency!
    insert_(names::V_m, 
	    &aeif_cond_exp_custom::get_y_elem_<aeif_cond_exp_custom::State_::V_M>);
    insert_(names::g_AMPA, 
	    &aeif_cond_exp_custom::get_y_elem_<aeif_cond_exp_custom::State_::G_AMPA>);
    insert_(names::g_NMDA, 
	    &aeif_cond_exp_custom::get_y_elem_<aeif_cond_exp_custom::State_::G_NMDA>);
    insert_(names::g_GABA_A, 
	    &aeif_cond_exp_custom::get_y_elem_<aeif_cond_exp_custom::State_::G_GABA_A>);
  }
}

//int nest::aeif_cond_exp_custom::evolve_substeps = 0;
//int nest::aeif_cond_exp_custom::evolve_N = 0;

extern "C"
int nest::aeif_cond_exp_custom_dynamics (double, const double y[], double f[], void* pnode)
{
  // a shorthand
  typedef nest::aeif_cond_exp_custom::State_ S;

  // get access to node so we can almost work as in a member function
  assert(pnode);
  const nest::aeif_cond_exp_custom& node =  *(reinterpret_cast<nest::aeif_cond_exp_custom*>(pnode));

  // y[] here is---and must be---the state vector supplied by the integrator,
  // not the state vector in the node, node.S_.y[]. 
  
  // The following code is verbose for the sake of clarity. We assume that a
  // good compiler will optimize the verbosity away ...

  // shorthand for state variables
  const double_t& V           = y[S::V_M  ];
  const double_t& g_AMPA      = y[S::G_AMPA];
  const double_t g_NMDA       = y[S::G_NMDA];
  const double_t g_GABA_A     = y[S::G_GABA_A];
  const double_t I_syn_AMPA   = g_AMPA   * (V - node.P.E_AMPA);
  const double_t I_syn_NMDA   = g_NMDA   * (V - node.P.E_NMDA);
  const double_t I_syn_GABA_A = g_GABA_A * (V - node.P.E_GABA_A);

  const double_t I_spike   = node.P.Delta_T * std::exp((V - node.P.V_th) / node.P.Delta_T);

  // dv/dt
  f[S::V_M  ] = ( -node.P.g_L * ( (V-node.P.E_L) - I_spike) 
		     - I_syn_AMPA - I_syn_NMDA - I_syn_GABA_A
             + node.P.I_e + node.B_.I_stim_) / node.P.C_m;

  f[S::G_AMPA]   = -g_AMPA   / node.P.tau_AMPA_fall; // Synaptic Conductance (nS)
  f[S::G_NMDA]   = -g_NMDA   / node.P.tau_NMDA_fall; // Synaptic Conductance (nS)
  f[S::G_GABA_A] = -g_GABA_A / node.P.tau_GABA_A_fall; // Synaptic Conductance (nS)

  return GSL_SUCCESS;
}

/* ---------------------------------------------------------------- 
 * Default constructors defining default parameters and state
 * ---------------------------------------------------------------- */
    
nest::aeif_cond_exp_custom::Parameters::Parameters()
  : V_peak          (   0.0 ), // mV
    V_reset         ( -60.0 ), // mV
    t_ref           (   0.0 ), // ms
    g_L             (  30.0 ), // nS
    C_m             ( 281.0 ), // pF
    E_L             ( -70.6 ), // mV
    E_AMPA          (   0.0 ), // mV
    E_NMDA          (   0.0 ), // mV
    E_GABA_A        ( -85.0 ), // mV
    Delta_T         (   2.0 ), // mV
    V_th            ( -50.4 ), // mV
    I_e             (   0.0 ), // pA
    tau_AMPA_fall   (   2.0 ), // ms
    tau_NMDA_rise   (   5.0 ), // ms
    tau_NMDA_fall   (  50.0 ), // ms
    tau_GABA_A_rise (   1.0 ), // ms
    tau_GABA_A_fall (   5.0 ), // ms
    tau_AHP         (  20.0 )  // ms
{
}

nest::aeif_cond_exp_custom::State_::State_(const Parameters &p)
  : r_(0)
{
  y_[0] = p.E_L;
  for ( size_t i = 1; i <STATE_VEC_SIZE; ++i )
    y_[i] = 0;
}

nest::aeif_cond_exp_custom::State_::State_(const State_ &s)
  : r_(s.r_)
{
  for ( size_t i = 0; i < STATE_VEC_SIZE; ++i )
    y_[i] = s.y_[i];
}

nest::aeif_cond_exp_custom::State_& nest::aeif_cond_exp_custom::State_::operator=(const State_ &s)
{
  assert(this != &s);  // would be bad logical error in program
  
  for ( size_t i = 0; i < STATE_VEC_SIZE; ++i )
    y_[i] = s.y_[i];
  r_ = s.r_;
  return *this;
}

/* ---------------------------------------------------------------- 
 * Paramater and state extractions and manipulation functions
 * ---------------------------------------------------------------- */

void nest::aeif_cond_exp_custom::Parameters::get(DictionaryDatum &d) const
{
  // ! Some of these names are locally defined as they are not part of NEST distribution
  def<double>(d, names::V_peak,     V_peak);
  def<double>(d, names::V_reset,    V_reset);
  def<double>(d, names::t_ref,      t_ref);

  def<double>(d, names::g_L,        g_L);
  def<double>(d, names::C_m,        C_m);
  def<double>(d, names::E_L,        E_L); 
  def<double>(d, names::E_AMPA,     E_AMPA); 
  def<double>(d, names::E_NMDA,     E_NMDA); 
  def<double>(d, names::E_GABA_A,   E_GABA_A); 
  def<double>(d, names::Delta_T,    Delta_T);
  def<double>(d, names::V_th,       V_th);
  def<double>(d, names::I_e,        I_e);

  def<double>(d, names::tau_AMPA_fall,   tau_AMPA_fall);
  def<double>(d, names::tau_NMDA_rise,   tau_NMDA_rise);
  def<double>(d, names::tau_NMDA_fall,   tau_NMDA_fall);
  def<double>(d, names::tau_GABA_A_rise, tau_GABA_A_rise);
  def<double>(d, names::tau_GABA_A_fall, tau_GABA_A_fall);

  def<double>(d, names::tau_AHP,         tau_AHP);
}

void nest::aeif_cond_exp_custom::Parameters::set(const DictionaryDatum &d)
{
  updateValue<double>(d, names::V_peak,     V_peak);
  updateValue<double>(d, names::V_reset,    V_reset);
  updateValue<double>(d, names::t_ref,      t_ref);

  updateValue<double>(d, names::g_L,        g_L);
  updateValue<double>(d, names::C_m,        C_m);
  updateValue<double>(d, names::E_L,        E_L); 
  updateValue<double>(d, names::E_AMPA,     E_AMPA); 
  updateValue<double>(d, names::E_NMDA,     E_NMDA); 
  updateValue<double>(d, names::E_GABA_A,   E_GABA_A); 
  updateValue<double>(d, names::Delta_T,    Delta_T);
  updateValue<double>(d, names::V_th,       V_th);
  updateValue<double>(d, names::I_e,        I_e);

  updateValue<double>(d, names::tau_AMPA_fall,   tau_AMPA_fall);
  updateValue<double>(d, names::tau_NMDA_rise,   tau_NMDA_rise);
  updateValue<double>(d, names::tau_NMDA_fall,   tau_NMDA_fall);
  updateValue<double>(d, names::tau_GABA_A_rise, tau_GABA_A_rise);
  updateValue<double>(d, names::tau_GABA_A_fall, tau_GABA_A_fall);

  updateValue<double>(d, names::tau_AHP,         tau_AHP);


  if ( V_reset >= V_peak )
    throw BadProperty("Reset potential must be smaller than spike cut-off threshold.");
    
  if ( V_peak <= V_th )
    throw BadProperty("V_peak must be larger than threshold.");

  if ( C_m <= 0 )
    throw BadProperty("Capacitance must be strictly positive.");
    
  if ( t_ref < 0 )
    throw BadProperty("Refractory time cannot be negative.");
      
  if ( tau_AMPA_fall <=0 || tau_NMDA_rise <= 0 || tau_NMDA_fall <= 0 ||
          tau_GABA_A_rise <= 0 || tau_GABA_A_fall <= 0 ||
          tau_AHP <= 0)
    throw BadProperty("All time constants must be strictly positive.");

  // TODO: check all other parameters
}

void nest::aeif_cond_exp_custom::State_::get(DictionaryDatum &d) const
{
  def<double>(d,names::V_m,      y_[V_M]);
  def<double>(d,names::g_AMPA,   y_[G_AMPA]);
  def<double>(d,names::g_NMDA,   y_[G_NMDA]);
  def<double>(d,names::g_GABA_A, y_[G_GABA_A]);
}

void nest::aeif_cond_exp_custom::State_::set(const DictionaryDatum &d, const Parameters &)
{
  updateValue<double>(d,names::V_m,      y_[V_M]);
  updateValue<double>(d,names::g_AMPA,   y_[G_AMPA]);
  updateValue<double>(d,names::g_NMDA,   y_[G_NMDA]);
  updateValue<double>(d,names::g_GABA_A, y_[G_GABA_A]);

  if ( y_[G_AMPA] < 0 || y_[G_NMDA] < 0 || y_[G_GABA_A] < 0 )
    throw BadProperty("Conductances must not be negative.");
}

nest::aeif_cond_exp_custom::Buffers_::Buffers_(aeif_cond_exp_custom &n)
  : logger_(n),
    spike_inputs_(std::vector<RingBuffer>(SYNAPSE_TYPES_SIZE))
{
  // Initialization of the remaining members is deferred to
  // init_buffers_().
}

nest::aeif_cond_exp_custom::Buffers_::Buffers_(const Buffers_ &, aeif_cond_exp_custom &n)
  : logger_(n),
    spike_inputs_(std::vector<RingBuffer>(SYNAPSE_TYPES_SIZE))
{
  // Initialization of the remaining members is deferred to
  // init_buffers_().
}

/* ---------------------------------------------------------------- 
 * Default and copy constructor for node, and destructor
 * ---------------------------------------------------------------- */

nest::aeif_cond_exp_custom::aeif_cond_exp_custom()
  : Archiving_Node(), 
    P(), 
    S_(P),
    B_(*this)
{
  recordablesMap_.create();
}

nest::aeif_cond_exp_custom::aeif_cond_exp_custom(const aeif_cond_exp_custom &n)
  : Archiving_Node(n), 
    P(n.P), 
    S_(n.S_),
    B_(n.B_, *this)
{
}

nest::aeif_cond_exp_custom::~aeif_cond_exp_custom()
{
}

/* ---------------------------------------------------------------- 
 * Node initialization functions
 * ---------------------------------------------------------------- */

void nest::aeif_cond_exp_custom::init_node_(const Node &proto)
{
  const aeif_cond_exp_custom &pr = downcast<aeif_cond_exp_custom>(proto);
  P = pr.P;
  S_ = pr.S_;
}

void nest::aeif_cond_exp_custom::init_state_(const Node &proto)
{
  const aeif_cond_exp_custom &pr = downcast<aeif_cond_exp_custom>(proto);
  S_ = pr.S_;
}

void nest::aeif_cond_exp_custom::init_buffers_()
{
  for (int i = 0; i < B_.spike_inputs_.size(); i++)
    B_.spike_inputs_[i].clear();

  B_.currents_.clear();           // includes resize
  Archiving_Node::clear_history();

  B_.logger_.reset();

  B_.step_ = Time::get_resolution().get_ms();

  B_.IntegrationStep_ = B_.step_; //std::min(0.01, B_.step_);

  B_.I_stim_ = 0.0;
}

void nest::aeif_cond_exp_custom::calibrate()
{
  B_.logger_.init();  // ensures initialization in case mm connected after Simulate
  V_.RefractoryCounts_ = Time(Time::ms(P.t_ref)).get_steps();
  assert(V_.RefractoryCounts_ >= 0);  // since t_ref >= 0, this can only fail in error
}

/* ---------------------------------------------------------------- 
 * Update and spike handling functions
 * ---------------------------------------------------------------- */

void nest::aeif_cond_exp_custom::update(const Time &origin, const long_t from, const long_t to)
{
  typedef nest::aeif_cond_exp_custom::State_ S;

  assert ( to >= 0 && (delay) from < Scheduler::get_min_delay() );
  assert ( from < to );
  assert ( State_::V_M == 0 );


  for ( long_t lag = from; lag < to; ++lag )
  {
    double t = 0.0;

    if ( S_.r_ > 0 )
      --S_.r_;

    // numerical integration using Explicit Euler: should be enough for our purpose
    while (t < B_.step_)
    {
      const int status = aeif_cond_exp_custom_dynamics(
              t,
              S_.y_,
              S_.dydt_,
              reinterpret_cast<void *>(this));

      //assert(S_.y_[S::G_GABA_A] >= 0);

      // Integrate, forward Euler
      for (int i = 0; i < S::STATE_VEC_SIZE; i++)
        S_.y_[i] += B_.IntegrationStep_ * S_.dydt_[i];

      if (S_.y_[S::G_GABA_A] < 0)
          std::cerr << S_.y_[S::G_GABA_A] << std::endl;

      if ( status != GSL_SUCCESS )
        throw GSLSolverFailure(get_name(), status);


      // check for unreasonable values; we allow V_M to explode
      if (S_.y_[State_::V_M] < -1e3)
        throw NumericalInstability(get_name());

      // spikes are handled inside the while-loop
      // due to spike-driven adaptation
      if ( S_.r_ > 0 )
        S_.y_[State_::V_M] = P.V_reset;
      else if ( S_.y_[State_::V_M] >= P.V_peak )
      {
        S_.y_[State_::V_M]  = P.V_reset;
        S_.r_               = V_.RefractoryCounts_;
        
        set_spiketime(Time::step(origin.get_steps() + lag + 1));
        SpikeEvent se;
        network()->send(*this, se, lag);
      }

      t += B_.IntegrationStep_;
    }

    // Process all spikes
    S_.y_[S::G_AMPA]   += B_.spike_inputs_[AMPA].get_value(lag);
    S_.y_[S::G_NMDA]   += B_.spike_inputs_[NMDA].get_value(lag);

    double_t gaba_spike = B_.spike_inputs_[GABA_A].get_value(lag);
    assert(gaba_spike >= 0);
    S_.y_[S::G_GABA_A] += gaba_spike;
      
    // set new input current
    B_.I_stim_ = B_.currents_.get_value(lag);

    // log state data
    B_.logger_.record_data(origin.get_steps() + lag);
  }
}
  
void nest::aeif_cond_exp_custom::handle(SpikeEvent &e)
{
  assert(e.get_delay() > 0);
  assert(e.get_weight() >= 0);
  assert(e.get_rport() < static_cast<int_t>(SYNAPSE_TYPES_SIZE));

  B_.spike_inputs_[e.get_rport()].
    add_value(e.get_rel_delivery_steps(network()->get_slice_origin()),
    e.get_weight() * e.get_multiplicity() );
}

void nest::aeif_cond_exp_custom::handle(CurrentEvent &e)
{
  assert ( e.get_delay() > 0 );

  const double_t c=e.get_current();
  const double_t w=e.get_weight();

  // add weighted current; HEP 2002-10-04
  B_.currents_.add_value(e.get_rel_delivery_steps(network()->get_slice_origin()), 
			 w*c);
}

void nest::aeif_cond_exp_custom::handle(DataLoggingRequest &e)
{
  B_.logger_.handle(e);
}

#endif // HAVE_GSL_1_11