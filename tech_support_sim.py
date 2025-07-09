import simpy
import random
import numpy as np
from collections import defaultdict
import argparse
import sys
import matplotlib.pyplot as plt

class TechSupportQueue:
    def __init__(self, env, num_agents, avg_call_duration=10, call_duration_std=3):
        self.env = env
        self.agents = simpy.PriorityResource(env, num_agents)
        self.avg_call_duration = avg_call_duration
        self.call_duration_std = call_duration_std
        
        # Metrics tracking
        self.customers_served = 0
        self.total_wait_time = 0
        self.total_service_time = 0
        self.wait_times = []
        self.service_times = []
        self.queue_lengths = []
        self.abandonments = 0
        
    def serve_customer(self, customer_id, priority=0, patience=30):
        """Process a customer call"""
        arrival_time = self.env.now
        print(f"Customer {customer_id} calls at time {arrival_time:.1f}")
        
        # Track queue length
        queue_length = len(self.agents.queue) + len(self.agents.users)
        self.queue_lengths.append((self.env.now, queue_length))
        
        # Customer tries to get an agent or abandons if wait is too long
        with self.agents.request(priority=priority) as request:
            # Race between getting service and running out of patience
            patience_timeout = self.env.timeout(patience)
            
            result = yield request | patience_timeout
            
            if request in result:
                # Customer got an agent
                wait_time = self.env.now - arrival_time
                self.wait_times.append(wait_time)
                self.total_wait_time += wait_time
                
                print(f"  Customer {customer_id} connected to agent at time {self.env.now:.1f} (waited {wait_time:.1f} min)")
                
                # Service time (normally distributed)
                service_time = max(1, np.random.normal(self.avg_call_duration, self.call_duration_std))
                self.service_times.append(service_time)
                self.total_service_time += service_time
                
                yield self.env.timeout(service_time)
                
                print(f"  Customer {customer_id} call completed at time {self.env.now:.1f} (service time: {service_time:.1f} min)")
                self.customers_served += 1
                
            else:
                # Customer abandoned (ran out of patience)
                print(f"  Customer {customer_id} abandoned at time {self.env.now:.1f} (waited {patience:.1f} min)")
                self.abandonments += 1

def customer_generator(env, support_queue, arrival_rate=0.5):
    """Generate customers calling the support line"""
    customer_id = 0
    while True:
        # Time until next customer (exponential distribution)
        inter_arrival_time = random.expovariate(arrival_rate)
        yield env.timeout(inter_arrival_time)
        
        customer_id += 1
        
        # Customer characteristics
        priority = 0  # Could be 1 for premium customers
        patience = random.uniform(15, 45)  # How long they'll wait (minutes)
        
        # Start serving the customer
        env.process(support_queue.serve_customer(customer_id, priority, patience))

def priority_customer_generator(env, support_queue, arrival_rate=0.1):
    """Generate priority customers (premium support)"""
    customer_id = 1000  # Start with high numbers to distinguish
    while True:
        inter_arrival_time = random.expovariate(arrival_rate)
        yield env.timeout(inter_arrival_time)
        
        customer_id += 1
        priority = 1  # Higher priority
        patience = random.uniform(20, 60)  # Premium customers wait longer
        
        print(f"PRIORITY Customer {customer_id} calls")
        env.process(support_queue.serve_customer(customer_id, priority, patience))

def queue_monitor(env, support_queue, interval=5):
    """Monitor and log queue statistics periodically"""
    while True:
        yield env.timeout(interval)
        queue_length = len(support_queue.agents.queue)
        busy_agents = len(support_queue.agents.users)
        print(f"[{env.now:.1f}] Queue: {queue_length}, Busy agents: {busy_agents}")

def run_simulation(sim_duration=480, num_agents=5, arrival_rate=0.8, avg_call_duration=8):
    """Run the tech support simulation"""
    print(f"=== Tech Support Queue Simulation ===")
    print(f"Simulation duration: {sim_duration} minutes ({sim_duration/60:.1f} hours)")
    print(f"Number of agents: {num_agents}")
    print(f"Customer arrival rate: {arrival_rate:.2f} customers/minute")
    print(f"Average call duration: {avg_call_duration} minutes")
    print()
    
    # Create simulation environment
    env = simpy.Environment()
    
    # Create support queue
    support_queue = TechSupportQueue(env, num_agents, avg_call_duration)
    
    # Start processes
    env.process(customer_generator(env, support_queue, arrival_rate))
    env.process(priority_customer_generator(env, support_queue, 0.1))
    env.process(queue_monitor(env, support_queue, 30))
    
    # Run simulation
    env.run(until=sim_duration)
    
    # Calculate and display results
    print(f"\n=== Simulation Results ===")
    print(f"Total customers served: {support_queue.customers_served}")
    print(f"Total abandonments: {support_queue.abandonments}")
    
    if support_queue.customers_served > 0:
        avg_wait = support_queue.total_wait_time / support_queue.customers_served
        avg_service = support_queue.total_service_time / support_queue.customers_served
        print(f"Average wait time: {avg_wait:.2f} minutes")
        print(f"Average service time: {avg_service:.2f} minutes")
        
        if support_queue.wait_times:
            print(f"Max wait time: {max(support_queue.wait_times):.2f} minutes")
            print(f"95th percentile wait time: {np.percentile(support_queue.wait_times, 95):.2f} minutes")
    
    total_customers = support_queue.customers_served + support_queue.abandonments
    if total_customers > 0:
        abandonment_rate = support_queue.abandonments / total_customers * 100
        print(f"Abandonment rate: {abandonment_rate:.1f}%")
    
    # Agent utilization
    total_service_time = sum(support_queue.service_times) if support_queue.service_times else 0
    total_agent_capacity = num_agents * sim_duration
    utilization = total_service_time / total_agent_capacity * 100
    print(f"Agent utilization: {utilization:.1f}%")
    
    return support_queue

# Example usage and scenarios
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tech Support Queue Simulation")
    parser.add_argument('--sim_duration', type=int, default=None, help='Simulation duration in minutes')
    parser.add_argument('--num_agents', type=int, default=None, help='Number of support agents')
    parser.add_argument('--arrival_rate', type=float, default=None, help='Customer arrival rate (customers per minute)')
    parser.add_argument('--avg_call_duration', type=float, default=None, help='Average call duration (minutes)')
    parser.add_argument('--plot', action='store_true', help='Show queue length chart after simulation')
    parser.add_argument('--save_plot', type=str, default=None, help='Save queue length chart to a PNG file (provide filename)')
    args = parser.parse_args()

    # If any simulation parameter is provided, run a single scenario with those parameters
    if any([args.sim_duration, args.num_agents, args.arrival_rate, args.avg_call_duration]):
        sim_duration = args.sim_duration if args.sim_duration is not None else 480
        num_agents = args.num_agents if args.num_agents is not None else 5
        arrival_rate = args.arrival_rate if args.arrival_rate is not None else 0.8
        avg_call_duration = args.avg_call_duration if args.avg_call_duration is not None else 8
        print("SCENARIO: Custom Parameters from Command Line")
        support_queue = run_simulation(sim_duration=sim_duration, num_agents=num_agents, arrival_rate=arrival_rate, avg_call_duration=avg_call_duration)
        if args.plot or args.save_plot:
            if support_queue.queue_lengths:
                times, lengths = zip(*support_queue.queue_lengths)
                plt.figure(figsize=(10, 5))
                plt.step(times, lengths, where='post')
                plt.xlabel('Time (minutes)')
                plt.ylabel('Queue Length')
                plt.title('Queue Length Over Time')
                plt.grid(True)
                plt.tight_layout()
                if args.save_plot:
                    plt.savefig(args.save_plot)
                    print(f"Queue length chart saved to {args.save_plot}")
                if args.plot:
                    plt.show()
                plt.close()
            else:
                print("No queue data to plot.")
    else:
        # Scenario 1: Normal operations
        print("SCENARIO 1: Normal Operations")
        run_simulation(sim_duration=480, num_agents=5, arrival_rate=0.6, avg_call_duration=8)
        print("\n" + "="*60 + "\n")
        # Scenario 2: High traffic period
        print("SCENARIO 2: High Traffic Period")
        run_simulation(sim_duration=240, num_agents=5, arrival_rate=1.2, avg_call_duration=8)
        print("\n" + "="*60 + "\n")
        # Scenario 3: Understaffed
        print("SCENARIO 3: Understaffed")
        run_simulation(sim_duration=240, num_agents=3, arrival_rate=0.8, avg_call_duration=10)