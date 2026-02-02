"""
Visualization Module for Simulation Results
"""

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any, Optional
import os
from scipy.interpolate import griddata

class Visualization:
    """Visualization class for simulation results"""
    
    def __init__(self, style: str = 'default'):
        self.style = style
        self.set_style()
    
    def set_style(self):
        """Set matplotlib style"""
        if self.style == 'seaborn':
            plt.style.use('seaborn-v0_8-darkgrid')
        else:
            plt.style.use('default')
        
        # Set default colors
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'error': '#d62728',
            'warning': '#ffbb78'
        }
    
    def create_pfr_sweep_3d(self, results: Dict[str, Any], save_path: str) -> bool:
        """Create 3D plot for PFR parametric sweep"""
        try:
            # Extract data from results
            if 'pfr' not in results:
                print("No PFR results found for 3D plot")
                return False
            
            pfr_data = results['pfr']
            if isinstance(pfr_data, dict) and 'sweep_results' in pfr_data:
                sweep_results = pfr_data['sweep_results']
            elif isinstance(pfr_data, list):
                sweep_results = pfr_data
            else:
                print("Invalid PFR results format")
                return False
            
            # Filter successful results
            successful_results = [r for r in sweep_results if r.get('success', False)]
            if len(successful_results) < 4:
                print(f"Not enough successful results ({len(successful_results)}) for 3D plot")
                return False
            
            # Extract data
            temperatures = []
            volumes = []
            conversions = []
            
            for result in successful_results:
                # Get temperature and volume from sweep parameters or reactor config
                if 'sweep_parameters' in result:
                    temp = result['sweep_parameters'].get('temperature', 
                           result.get('reactor_temperature', 350))
                    vol = result['sweep_parameters'].get('volume',
                          result.get('reactor_volume', 1.0))
                else:
                    temp = result.get('reactor_temperature', 350)
                    vol = result.get('reactor_volume', 1.0)
                
                conversion = result.get('conversion_percent', 0)
                
                temperatures.append(temp)
                volumes.append(vol)
                conversions.append(conversion)
            
            # Create grid for surface
            if len(set(temperatures)) > 1 and len(set(volumes)) > 1:
                # Create grid
                xi = np.linspace(min(temperatures), max(temperatures), 50)
                yi = np.linspace(min(volumes), max(volumes), 50)
                xi, yi = np.meshgrid(xi, yi)
                
                # Interpolate
                zi = griddata((temperatures, volumes), conversions, (xi, yi), method='cubic')
                
                # Create 3D plot
                fig = plt.figure(figsize=(12, 8))
                ax = fig.add_subplot(111, projection='3d')
                
                # Plot surface
                surf = ax.plot_surface(xi, yi, zi, cmap=cm.viridis, 
                                      alpha=0.8, linewidth=0, antialiased=True)
                
                # Plot scatter points
                ax.scatter(temperatures, volumes, conversions, 
                          c='red', s=50, alpha=0.8, label='Simulation Points')
                
                # Labels and title
                ax.set_xlabel('Temperature (K)', fontsize=12, labelpad=10)
                ax.set_ylabel('Reactor Volume (m³)', fontsize=12, labelpad=10)
                ax.set_zlabel('Conversion (%)', fontsize=12, labelpad=10)
                ax.set_title('PFR: Conversion vs Temperature and Volume', fontsize=14, pad=20)
                
                # Colorbar
                fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label='Conversion (%)')
                
                # Add legend
                ax.legend()
                
                # Adjust view
                ax.view_init(elev=30, azim=45)
                
                # Save figure
                plt.tight_layout()
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"✅ 3D PFR plot saved: {save_path}")
                return True
            else:
                print("Insufficient data variation for 3D plot")
                return False
                
        except Exception as e:
            print(f"❌ Failed to create 3D PFR plot: {str(e)}")
            return False
    
    def create_distillation_optimization(self, results: Dict[str, Any], save_path: str) -> bool:
        """Create optimization plots for distillation column"""
        try:
            # Extract data from results
            if 'distillation' not in results:
                print("No distillation results found")
                return False
            
            dist_data = results['distillation']
            if isinstance(dist_data, dict) and 'sweep_results' in dist_data:
                sweep_results = dist_data['sweep_results']
            elif isinstance(dist_data, list):
                sweep_results = dist_data
            else:
                print("Invalid distillation results format")
                return False
            
            # Filter successful and converged results
            successful_results = [r for r in sweep_results 
                                if r.get('success', False) and r.get('converged', False)]
            if len(successful_results) < 3:
                print(f"Not enough successful results ({len(successful_results)})")
                return False
            
            # Extract data
            reflux_ratios = []
            stages_list = []
            purities = []
            energies = []
            
            for result in successful_results:
                # Get parameters
                if 'sweep_parameters' in result:
                    rr = result['sweep_parameters'].get('reflux_ratio', 
                         result.get('reflux_ratio', 2.0))
                    stages = result['sweep_parameters'].get('stages',
                            result.get('column_stages', 10))
                else:
                    rr = result.get('reflux_ratio', 2.0)
                    stages = result.get('column_stages', 10)
                
                purity = result.get('distillate_purity_A', 0)
                energy = result.get('total_energy', 0)
                
                reflux_ratios.append(rr)
                stages_list.append(stages)
                purities.append(purity)
                energies.append(energy)
            
            # Create subplots
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            axes = axes.flatten()
            
            # Plot 1: Purity vs Reflux Ratio
            ax1 = axes[0]
            unique_stages = sorted(set(stages_list))
            colors = plt.cm.Set3(np.linspace(0, 1, len(unique_stages)))
            
            for i, stage in enumerate(unique_stages):
                mask = [s == stage for s in stages_list]
                rr_stage = [rr for rr, m in zip(reflux_ratios, mask) if m]
                purity_stage = [p for p, m in zip(purities, mask) if m]
                
                if rr_stage and purity_stage:
                    # Sort for proper line plotting
                    sorted_data = sorted(zip(rr_stage, purity_stage))
                    rr_sorted, purity_sorted = zip(*sorted_data)
                    
                    ax1.plot(rr_sorted, purity_sorted, 'o-', color=colors[i], 
                            linewidth=2, markersize=8, label=f'{stage} stages')
            
            ax1.set_xlabel('Reflux Ratio', fontsize=12)
            ax1.set_ylabel('Distillate Purity A (%)', fontsize=12)
            ax1.set_title('Purity vs Reflux Ratio', fontsize=14)
            ax1.grid(True, alpha=0.3)
            ax1.legend(title='Number of Stages', fontsize=10)
            
            # Plot 2: Energy vs Reflux Ratio
            ax2 = axes[1]
            for i, stage in enumerate(unique_stages):
                mask = [s == stage for s in stages_list]
                rr_stage = [rr for rr, m in zip(reflux_ratios, mask) if m]
                energy_stage = [e for e, m in zip(energies, mask) if m]
                
                if rr_stage and energy_stage:
                    # Sort for proper line plotting
                    sorted_data = sorted(zip(rr_stage, energy_stage))
                    rr_sorted, energy_sorted = zip(*sorted_data)
                    
                    ax2.plot(rr_sorted, energy_sorted, 's-', color=colors[i], 
                            linewidth=2, markersize=8, label=f'{stage} stages')
            
            ax2.set_xlabel('Reflux Ratio', fontsize=12)
            ax2.set_ylabel('Total Energy (kW)', fontsize=12)
            ax2.set_title('Energy Consumption vs Reflux Ratio', fontsize=14)
            ax2.grid(True, alpha=0.3)
            ax2.legend(title='Number of Stages', fontsize=10)
            
            # Plot 3: Purity vs Stages
            ax3 = axes[2]
            unique_rr = sorted(set(reflux_ratios))
            colors_rr = plt.cm.Set2(np.linspace(0, 1, len(unique_rr)))
            
            for i, rr in enumerate(unique_rr):
                mask = [r == rr for r in reflux_ratios]
                stages_rr = [s for s, m in zip(stages_list, mask) if m]
                purity_rr = [p for p, m in zip(purities, mask) if m]
                
                if stages_rr and purity_rr:
                    # Sort for proper line plotting
                    sorted_data = sorted(zip(stages_rr, purity_rr))
                    stages_sorted, purity_sorted = zip(*sorted_data)
                    
                    ax3.plot(stages_sorted, purity_sorted, 'D-', color=colors_rr[i], 
                            linewidth=2, markersize=8, label=f'RR={rr:.1f}')
            
            ax3.set_xlabel('Number of Stages', fontsize=12)
            ax3.set_ylabel('Distillate Purity A (%)', fontsize=12)
            ax3.set_title('Purity vs Number of Stages', fontsize=14)
            ax3.grid(True, alpha=0.3)
            ax3.legend(title='Reflux Ratio', fontsize=10)
            
            # Plot 4: Contour plot of purity
            ax4 = axes[3]
            if len(set(reflux_ratios)) > 2 and len(set(stages_list)) > 2:
                # Create grid data
                xi = np.linspace(min(reflux_ratios), max(reflux_ratios), 50)
                yi = np.linspace(min(stages_list), max(stages_list), 50)
                xi, yi = np.meshgrid(xi, yi)
                
                # Interpolate
                zi = griddata((reflux_ratios, stages_list), purities, (xi, yi), method='cubic')
                
                # Create contour plot
                contour = ax4.contourf(xi, yi, zi, levels=20, cmap='YlOrRd', alpha=0.8)
                
                # Add contour lines
                ax4.contour(xi, yi, zi, levels=10, colors='black', alpha=0.5, linewidths=0.5)
                
                # Add scatter points
                ax4.scatter(reflux_ratios, stages_list, c=purities, 
                          cmap='YlOrRd', s=50, edgecolors='black', alpha=0.8)
                
                ax4.set_xlabel('Reflux Ratio', fontsize=12)
                ax4.set_ylabel('Number of Stages', fontsize=12)
                ax4.set_title('Purity Contour Plot', fontsize=14)
                
                # Add colorbar
                plt.colorbar(contour, ax=ax4, label='Purity (%)')
            else:
                # If not enough data for contour, create bar chart of optimal cases
                ax4.text(0.5, 0.5, 'Insufficient data for contour plot\nUsing summary instead',
                        ha='center', va='center', transform=ax4.transAxes, fontsize=12)
                ax4.set_title('Data Summary', fontsize=14)
                ax4.axis('off')
            
            # Adjust layout
            plt.suptitle('Distillation Column Optimization Analysis', fontsize=16, y=0.98)
            plt.tight_layout()
            
            # Save figure
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Distillation optimization plot saved: {save_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create distillation optimization plot: {str(e)}")
            return False
    
    def create_sensitivity_analysis(self, results: Dict[str, Any], save_path: str) -> bool:
        """Create sensitivity analysis plots"""
        try:
            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            axes = axes.flatten()
            
            # Plot 1: PFR Conversion Distribution
            ax1 = axes[0]
            if 'pfr' in results:
                pfr_data = results['pfr']
                if isinstance(pfr_data, dict) and 'sweep_results' in pfr_data:
                    sweep_results = pfr_data['sweep_results']
                elif isinstance(pfr_data, list):
                    sweep_results = pfr_data
                else:
                    sweep_results = []
                
                # Filter successful results
                successful_results = [r for r in sweep_results if r.get('success', False)]
                conversions = [r.get('conversion_percent', 0) for r in successful_results]
                
                if conversions:
                    ax1.hist(conversions, bins=15, color=self.colors['primary'], 
                            alpha=0.7, edgecolor='black')
                    ax1.axvline(np.mean(conversions), color='red', linestyle='--', 
                               linewidth=2, label=f'Mean: {np.mean(conversions):.1f}%')
                    ax1.set_xlabel('Conversion (%)', fontsize=12)
                    ax1.set_ylabel('Frequency', fontsize=12)
                    ax1.set_title('PFR Conversion Distribution', fontsize=14)
                    ax1.legend()
                    ax1.grid(True, alpha=0.3)
                else:
                    ax1.text(0.5, 0.5, 'No PFR data', ha='center', va='center', 
                            transform=ax1.transAxes, fontsize=12)
                    ax1.set_title('PFR Conversion Distribution', fontsize=14)
            else:
                ax1.text(0.5, 0.5, 'No PFR data', ha='center', va='center', 
                        transform=ax1.transAxes, fontsize=12)
                ax1.set_title('PFR Conversion Distribution', fontsize=14)
            
            # Plot 2: Distillation Purity Distribution
            ax2 = axes[1]
            if 'distillation' in results:
                dist_data = results['distillation']
                if isinstance(dist_data, dict) and 'sweep_results' in dist_data:
                    sweep_results = dist_data['sweep_results']
                elif isinstance(dist_data, list):
                    sweep_results = dist_data
                else:
                    sweep_results = []
                
                # Filter successful and converged results
                successful_results = [r for r in sweep_results 
                                    if r.get('success', False) and r.get('converged', False)]
                purities = [r.get('distillate_purity_A', 0) for r in successful_results]
                
                if purities:
                    ax2.hist(purities, bins=15, color=self.colors['secondary'], 
                            alpha=0.7, edgecolor='black')
                    ax2.axvline(np.mean(purities), color='red', linestyle='--', 
                               linewidth=2, label=f'Mean: {np.mean(purities):.1f}%')
                    ax2.set_xlabel('Distillate Purity A (%)', fontsize=12)
                    ax2.set_ylabel('Frequency', fontsize=12)
                    ax2.set_title('Distillation Purity Distribution', fontsize=14)
                    ax2.legend()
                    ax2.grid(True, alpha=0.3)
                else:
                    ax2.text(0.5, 0.5, 'No distillation data', ha='center', va='center', 
                            transform=ax2.transAxes, fontsize=12)
                    ax2.set_title('Distillation Purity Distribution', fontsize=14)
            else:
                ax2.text(0.5, 0.5, 'No distillation data', ha='center', va='center', 
                        transform=ax2.transAxes, fontsize=12)
                ax2.set_title('Distillation Purity Distribution', fontsize=14)
            
            # Plot 3: Success Rate Comparison
            ax3 = axes[2]
            categories = ['PFR', 'Distillation']
            success_rates = []
            
            # Calculate PFR success rate
            if 'pfr' in results:
                pfr_data = results['pfr']
                if isinstance(pfr_data, dict) and 'sweep_results' in pfr_data:
                    sweep_results = pfr_data['sweep_results']
                elif isinstance(pfr_data, list):
                    sweep_results = pfr_data
                else:
                    sweep_results = []
                
                if sweep_results:
                    successful = sum(1 for r in sweep_results if r.get('success', False))
                    success_rates.append(successful / len(sweep_results) * 100)
                else:
                    success_rates.append(0)
            else:
                success_rates.append(0)
            
            # Calculate distillation success rate
            if 'distillation' in results:
                dist_data = results['distillation']
                if isinstance(dist_data, dict) and 'sweep_results' in dist_data:
                    sweep_results = dist_data['sweep_results']
                elif isinstance(dist_data, list):
                    sweep_results = dist_data
                else:
                    sweep_results = []
                
                if sweep_results:
                    successful = sum(1 for r in sweep_results 
                                   if r.get('success', False) and r.get('converged', False))
                    success_rates.append(successful / len(sweep_results) * 100)
                else:
                    success_rates.append(0)
            else:
                success_rates.append(0)
            
            # Create bar chart
            bars = ax3.bar(categories, success_rates, color=[self.colors['primary'], 
                                                           self.colors['secondary']])
            ax3.set_ylabel('Success Rate (%)', fontsize=12)
            ax3.set_title('Simulation Success Rates', fontsize=14)
            ax3.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for bar, rate in zip(bars, success_rates):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{rate:.1f}%', ha='center', va='bottom', fontsize=11)
            
            # Plot 4: Performance Metrics
            ax4 = axes[3]
            metrics = ['Avg Solve Time', 'Max Conversion', 'Max Purity']
            values = []
            
            # Calculate average solve time
            solve_times = []
            if 'pfr' in results:
                pfr_data = results['pfr']
                if isinstance(pfr_data, dict) and 'sweep_results' in pfr_data:
                    sweep_results = pfr_data['sweep_results']
                elif isinstance(pfr_data, list):
                    sweep_results = pfr_data
                else:
                    sweep_results = []
                
                solve_times.extend([r.get('solve_time', 0) for r in sweep_results 
                                  if r.get('success', False)])
            
            if 'distillation' in results:
                dist_data = results['distillation']
                if isinstance(dist_data, dict) and 'sweep_results' in dist_data:
                    sweep_results = dist_data['sweep_results']
                elif isinstance(dist_data, list):
                    sweep_results = dist_data
                else:
                    sweep_results = []
                
                solve_times.extend([r.get('solve_time', 0) for r in sweep_results 
                                  if r.get('success', False) and r.get('converged', False)])
            
            if solve_times:
                values.append(np.mean(solve_times))
            else:
                values.append(0)
            
            # Calculate max conversion
            max_conversion = 0
            if 'pfr' in results:
                pfr_data = results['pfr']
                if isinstance(pfr_data, dict) and 'sweep_results' in pfr_data:
                    sweep_results = pfr_data['sweep_results']
                elif isinstance(pfr_data, list):
                    sweep_results = pfr_data
                else:
                    sweep_results = []
                
                for r in sweep_results:
                    if r.get('success', False):
                        max_conversion = max(max_conversion, r.get('conversion_percent', 0))
            
            values.append(max_conversion)
            
            # Calculate max purity
            max_purity = 0
            if 'distillation' in results:
                dist_data = results['distillation']
                if isinstance(dist_data, dict) and 'sweep_results' in dist_data:
                    sweep_results = dist_data['sweep_results']
                elif isinstance(dist_data, list):
                    sweep_results = dist_data
                else:
                    sweep_results = []
                
                for r in sweep_results:
                    if r.get('success', False) and r.get('converged', False):
                        max_purity = max(max_purity, r.get('distillate_purity_A', 0))
            
            values.append(max_purity)
            
            # Create bar chart
            colors_metrics = [self.colors['primary'], self.colors['success'], 
                            self.colors['secondary']]
            bars = ax4.bar(metrics, values, color=colors_metrics)
            ax4.set_ylabel('Value', fontsize=12)
            ax4.set_title('Performance Metrics', fontsize=14)
            ax4.grid(True, alpha=0.3, axis='y')
            
            # Add value labels
            for bar, value in zip(bars, values):
                height = bar.get_height()
                if metrics[bars.index(bar)] == 'Avg Solve Time':
                    label = f'{value:.2f}s'
                else:
                    label = f'{value:.1f}%'
                ax4.text(bar.get_x() + bar.get_width()/2., height + (0.02 * max(values)),
                        label, ha='center', va='bottom', fontsize=11)
            
            # Adjust layout
            plt.suptitle('Sensitivity Analysis and Performance Metrics', fontsize=16, y=0.98)
            plt.tight_layout()
            
            # Save figure
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Sensitivity analysis plot saved: {save_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create sensitivity analysis plot: {str(e)}")
            return False
    
    def create_all_plots(self, results: Dict[str, Any], output_dir: str) -> Dict[str, bool]:
        """Create all visualization plots"""
        plot_results = {}
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Create PFR 3D plot
        pfr_3d_path = os.path.join(output_dir, 'pfr_sweep_3d.png')
        plot_results['pfr_3d'] = self.create_pfr_sweep_3d(results, pfr_3d_path)
        
        # Create distillation optimization plot
        dist_opt_path = os.path.join(output_dir, 'distillation_optimization.png')
        plot_results['distillation_optimization'] = self.create_distillation_optimization(results, dist_opt_path)
        
        # Create sensitivity analysis plot
        sensitivity_path = os.path.join(output_dir, 'sensitivity_analysis.png')
        plot_results['sensitivity_analysis'] = self.create_sensitivity_analysis(results, sensitivity_path)
        
        # Summary
        successful_plots = sum(plot_results.values())
        total_plots = len(plot_results)
        
        print(f"📊 Plot generation summary: {successful_plots}/{total_plots} successful")
        
        return plot_results
    
    def create_interactive_plot(self, results: Dict[str, Any], output_path: str) -> bool:
        """Create interactive Plotly visualization (optional)"""
        try:
            # This would create an interactive HTML plot using Plotly
            # For now, just create a placeholder
            print("Interactive plots require Plotly and would be saved as HTML files")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create interactive plot: {str(e)}")
            return False