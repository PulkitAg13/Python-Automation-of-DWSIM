"""
Results Manager for handling simulation outputs
"""

import pandas as pd
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from pathlib import Path

class ResultsManager:
    """Manager for simulation results"""
    
    def __init__(self):
        self.results = {}
        
    def save_to_csv(self, results: Dict[str, Any], filename: str) -> bool:
        """Save results to CSV file"""
        try:
            # Extract all data rows
            rows = []
            
            # Add PFR results
            if 'pfr' in results:
                pfr_data = results['pfr']
                if isinstance(pfr_data, dict) and 'sweep_results' in pfr_data:
                    for result in pfr_data['sweep_results']:
                        rows.append(self._extract_pfr_row(result, 'sweep'))
                elif isinstance(pfr_data, list):
                    for result in pfr_data:
                        rows.append(self._extract_pfr_row(result, 'sweep'))
                elif isinstance(pfr_data, dict) and 'base_case' in pfr_data:
                    rows.append(self._extract_pfr_row(pfr_data['base_case'], 'base'))
            
            # Add distillation results
            if 'distillation' in results:
                dist_data = results['distillation']
                if isinstance(dist_data, dict) and 'sweep_results' in dist_data:
                    for result in dist_data['sweep_results']:
                        rows.append(self._extract_dist_row(result, 'sweep'))
                elif isinstance(dist_data, list):
                    for result in dist_data:
                        rows.append(self._extract_dist_row(result, 'sweep'))
                elif isinstance(dist_data, dict) and 'base_case' in dist_data:
                    rows.append(self._extract_dist_row(dist_data['base_case'], 'base'))
            
            # Add metadata
            if 'metadata' in results:
                for row in rows:
                    row.update(results['metadata'])
            
            # Create DataFrame and save
            if rows:
                df = pd.DataFrame(rows)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                
                # Save to CSV
                df.to_csv(filename, index=False)
                print(f"✅ Results saved to CSV: {filename}")
                return True
            else:
                print("⚠️ No results to save")
                return False
                
        except Exception as e:
            print(f"❌ Failed to save CSV: {str(e)}")
            return False
    
    def _extract_pfr_row(self, result: Dict, case_type: str) -> Dict:
        """Extract PFR result row"""
        row = {
            'simulation_type': 'pfr',
            'case_type': case_type,
            'success': result.get('success', False),
            'conversion_percent': result.get('conversion_percent', 0),
            'b_production_rate': result.get('b_production_rate', 0),
            'outlet_temperature': result.get('outlet_temperature', 0),
            'heat_duty': result.get('heat_duty', 0),
            'reactor_volume': result.get('reactor_volume', 0),
            'reactor_temperature': result.get('reactor_temperature', 0),
            'solve_time': result.get('solve_time', 0),
            'timestamp': result.get('timestamp', ''),
            'error': result.get('error', '')
        }
        
        # Add sweep parameters
        if 'sweep_parameters' in result:
            for key, value in result['sweep_parameters'].items():
                row[f'sweep_{key}'] = value
        
        return row
    
    def _extract_dist_row(self, result: Dict, case_type: str) -> Dict:
        """Extract distillation result row"""
        row = {
            'simulation_type': 'distillation',
            'case_type': case_type,
            'success': result.get('success', False),
            'converged': result.get('converged', False),
            'distillate_purity_A': result.get('distillate_purity_A', 0),
            'bottoms_purity_B': result.get('bottoms_purity_B', 0),
            'condenser_duty': result.get('condenser_duty', 0),
            'reboiler_duty': result.get('reboiler_duty', 0),
            'total_energy': result.get('total_energy', 0),
            'column_stages': result.get('column_stages', 0),
            'feed_stage': result.get('feed_stage', 0),
            'reflux_ratio': result.get('reflux_ratio', 0),
            'solve_time': result.get('solve_time', 0),
            'timestamp': result.get('timestamp', ''),
            'error': result.get('error', '')
        }
        
        # Add sweep parameters
        if 'sweep_parameters' in result:
            for key, value in result['sweep_parameters'].items():
                row[f'sweep_{key}'] = value
        
        return row
    
    def save_to_json(self, results: Dict[str, Any], filename: str, 
                    data_type: str = 'all') -> bool:
        """Save results to JSON file"""
        try:
            # Filter data if needed
            if data_type == 'pfr' and 'pfr' in results:
                data_to_save = results['pfr']
            elif data_type == 'distillation' and 'distillation' in results:
                data_to_save = results['distillation']
            else:
                data_to_save = results
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Save to JSON
            with open(filename, 'w') as f:
                json.dump(data_to_save, f, indent=2, default=str)
            
            print(f"✅ Results saved to JSON: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save JSON: {str(e)}")
            return False
    
    def generate_html_report(self, results: Dict[str, Any], filename: str) -> bool:
        """Generate HTML report from results"""
        try:
            # Create HTML content
            html_content = self._create_html_content(results)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Save HTML file
            with open(filename, 'w') as f:
                f.write(html_content)
            
            print(f"✅ HTML report generated: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate HTML report: {str(e)}")
            return False
    
    def _create_html_content(self, results: Dict[str, Any]) -> str:
        """Create HTML report content"""
        # Get metadata
        metadata = results.get('metadata', {})
        
        # Count successful cases
        pfr_success = 0
        dist_success = 0
        
        if 'pfr' in results:
            pfr_data = results['pfr']
            if isinstance(pfr_data, dict) and 'sweep_results' in pfr_data:
                pfr_success = sum(1 for r in pfr_data['sweep_results'] if r.get('success', False))
            elif isinstance(pfr_data, list):
                pfr_success = sum(1 for r in pfr_data if r.get('success', False))
        
        if 'distillation' in results:
            dist_data = results['distillation']
            if isinstance(dist_data, dict) and 'sweep_results' in dist_data:
                dist_success = sum(1 for r in dist_data['sweep_results'] if r.get('success', False) and r.get('converged', False))
            elif isinstance(dist_data, list):
                dist_success = sum(1 for r in dist_data if r.get('success', False) and r.get('converged', False))
        
        # Create HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>DWSIM Simulation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
        .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff; }}
        .success {{ color: #28a745; }}
        .error {{ color: #dc3545; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f8f9fa; }}
        tr:hover {{ background-color: #f5f5f5; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>DWSIM Simulation Report</h1>
        <p>Generated on: {metadata.get('timestamp', 'N/A')}</p>
        <p>Execution time: {metadata.get('execution_time', 'N/A')}</p>
    </div>
    
    <div class="section">
        <h2>📊 Simulation Summary</h2>
        <div class="stats">
            <div class="stat-card">
                <h3>PFR Simulations</h3>
                <p class="success">Successful: {pfr_success}</p>
            </div>
            <div class="stat-card">
                <h3>Distillation Simulations</h3>
                <p class="success">Successful: {dist_success}</p>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>🧪 PFR Reactor Results</h2>
        <p>Base case and parametric sweep results for Plug Flow Reactor.</p>
        <p>Check <code>pfr_results.json</code> for detailed data.</p>
    </div>
    
    <div class="section">
        <h2>🏭 Distillation Column Results</h2>
        <p>Base case and parametric sweep results for Distillation Column.</p>
        <p>Check <code>distillation_results.json</code> for detailed data.</p>
    </div>
    
    <div class="section">
        <h2>📈 Generated Plots</h2>
        <p>The following plots have been generated:</p>
        <ul>
            <li><strong>pfr_sweep_3d.png</strong>: 3D surface plot of PFR conversion vs temperature and volume</li>
            <li><strong>distillation_optimization.png</strong>: Optimization plots for distillation column</li>
            <li><strong>sensitivity_analysis.png</strong>: Sensitivity analysis plots</li>
        </ul>
        <p>All plots are available in the <code>results/plots/</code> directory.</p>
    </div>
    
    <div class="section">
        <h2>📁 Output Files</h2>
        <table>
            <tr>
                <th>File</th>
                <th>Description</th>
                <th>Format</th>
            </tr>
            <tr>
                <td><code>results.csv</code></td>
                <td>Main simulation results</td>
                <td>CSV</td>
            </tr>
            <tr>
                <td><code>pfr_results.json</code></td>
                <td>Detailed PFR simulation data</td>
                <td>JSON</td>
            </tr>
            <tr>
                <td><code>distillation_results.json</code></td>
                <td>Detailed distillation simulation data</td>
                <td>JSON</td>
            </tr>
            <tr>
                <td><code>results_summary.html</code></td>
                <td>This report</td>
                <td>HTML</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>⚙️ Configuration Used</h2>
        <p>Simulations were run using configurations from:</p>
        <ul>
            <li><code>config/pfr_config.yaml</code> - PFR reactor settings</li>
            <li><code>config/distillation_config.yaml</code> - Distillation column settings</li>
            <li><code>config/sweep_config.yaml</code> - Parametric sweep settings</li>
        </ul>
    </div>
    
    <footer style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; color: #666;">
        <p>Generated by DWSIM Automation Tool v1.0.0</p>
        <p>Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </footer>
</body>
</html>
        """
        
        return html
    
    def validate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate simulation results"""
        validation = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Check PFR results
        if 'pfr' in results:
            pfr_data = results['pfr']
            if isinstance(pfr_data, dict) and 'base_case' in pfr_data:
                base_result = pfr_data['base_case']
                if base_result.get('success', False):
                    # Check conversion range
                    conversion = base_result.get('conversion_percent', 0)
                    if conversion < 0 or conversion > 100:
                        validation['warnings'].append(f'PFR conversion out of range: {conversion}%')
                else:
                    validation['errors'].append('PFR base case failed')
        
        # Check distillation results
        if 'distillation' in results:
            dist_data = results['distillation']
            if isinstance(dist_data, dict) and 'base_case' in dist_data:
                base_result = dist_data['base_case']
                if base_result.get('success', False) and base_result.get('converged', False):
                    # Check purity range
                    purity = base_result.get('distillate_purity_A', 0)
                    if purity < 0 or purity > 100:
                        validation['warnings'].append(f'Distillate purity out of range: {purity}%')
                else:
                    validation['errors'].append('Distillation base case failed or did not converge')
        
        # Update validation status
        if validation['errors']:
            validation['valid'] = False
        
        return validation