#!/usr/bin/env python3
"""
Script para ejecutar tests de integración del sistema Karl AI Ecosystem
"""

import subprocess
import sys
import time
import requests
from pathlib import Path
from typing import List, Dict, Any


class IntegrationTestRunner:
    """Ejecutor de tests de integración"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.api_url = "http://localhost:8000"
        self.test_results = []
        
    def check_api_availability(self) -> bool:
        """Verificar si la API está disponible"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def run_pytest_tests(self, test_files: List[str]) -> Dict[str, Any]:
        """Ejecutar tests con pytest"""
        results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "total": 0,
            "duration": 0
        }
        
        start_time = time.time()
        
        for test_file in test_files:
            print(f"\n🧪 Ejecutando tests en {test_file}...")
            
            try:
                # Ejecutar pytest para el archivo específico
                cmd = [
                    sys.executable, "-m", "pytest", 
                    str(self.project_root / test_file),
                    "-v", "--tb=short", "--no-header"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
                
                # Parsear resultados
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if "passed" in line and "failed" in line:
                        # Extraer números de la línea de resumen
                        parts = line.split()
                        for part in parts:
                            if part.isdigit():
                                if "passed" in line:
                                    results["passed"] += int(part)
                                elif "failed" in line:
                                    results["failed"] += int(part)
                                elif "skipped" in line:
                                    results["skipped"] += int(part)
                
                if result.returncode != 0:
                    print(f"❌ Tests fallaron en {test_file}")
                    print(f"Error: {result.stderr}")
                else:
                    print(f"✅ Tests pasaron en {test_file}")
                
            except Exception as e:
                print(f"❌ Error ejecutando tests en {test_file}: {e}")
                results["errors"] += 1
        
        end_time = time.time()
        results["duration"] = end_time - start_time
        results["total"] = results["passed"] + results["failed"] + results["skipped"] + results["errors"]
        
        return results
    
    def run_monitoring_tests(self) -> Dict[str, Any]:
        """Ejecutar tests de monitoreo"""
        print("\n📊 Ejecutando tests de monitoreo...")
        
        test_files = [
            "corehub/tests/test_monitoring.py"
        ]
        
        return self.run_pytest_tests(test_files)
    
    def run_devagent_tests(self) -> Dict[str, Any]:
        """Ejecutar tests de DevAgent"""
        print("\n🤖 Ejecutando tests de DevAgent...")
        
        test_files = [
            "agents/devagent/tests/test_integration.py"
        ]
        
        return self.run_pytest_tests(test_files)
    
    def run_system_tests(self) -> Dict[str, Any]:
        """Ejecutar tests del sistema completo"""
        print("\n🔧 Ejecutando tests del sistema completo...")
        
        test_files = [
            "tests/test_system_integration.py"
        ]
        
        return self.run_pytest_tests(test_files)
    
    def run_api_tests(self) -> Dict[str, Any]:
        """Ejecutar tests de API"""
        print("\n🌐 Ejecutando tests de API...")
        
        if not self.check_api_availability():
            print("⚠️ API no disponible, saltando tests de API")
            return {
                "passed": 0,
                "failed": 0,
                "skipped": 1,
                "errors": 0,
                "total": 1,
                "duration": 0
            }
        
        # Tests de API específicos
        api_tests = [
            "corehub/tests/test_api_health.py",
            "corehub/tests/test_api_events.py",
            "corehub/tests/test_api_tasks.py",
            "corehub/tests/test_api_report.py"
        ]
        
        return self.run_pytest_tests(api_tests)
    
    def generate_report(self, all_results: Dict[str, Dict[str, Any]]) -> str:
        """Generar reporte de tests"""
        total_passed = sum(results["passed"] for results in all_results.values())
        total_failed = sum(results["failed"] for results in all_results.values())
        total_skipped = sum(results["skipped"] for results in all_results.values())
        total_errors = sum(results["errors"] for results in all_results.values())
        total_duration = sum(results["duration"] for results in all_results.values())
        
        report = f"""
# 📊 Reporte de Tests de Integración - Karl AI Ecosystem

## 📈 Resumen General
- **Tests Pasados**: {total_passed}
- **Tests Fallidos**: {total_failed}
- **Tests Saltados**: {total_skipped}
- **Errores**: {total_errors}
- **Duración Total**: {total_duration:.2f} segundos
- **Tasa de Éxito**: {(total_passed / (total_passed + total_failed) * 100):.1f}%

## 📋 Resultados por Categoría

### 🔧 Tests del Sistema
- Pasados: {all_results.get('system', {}).get('passed', 0)}
- Fallidos: {all_results.get('system', {}).get('failed', 0)}
- Saltados: {all_results.get('system', {}).get('skipped', 0)}
- Duración: {all_results.get('system', {}).get('duration', 0):.2f}s

### 📊 Tests de Monitoreo
- Pasados: {all_results.get('monitoring', {}).get('passed', 0)}
- Fallidos: {all_results.get('monitoring', {}).get('failed', 0)}
- Saltados: {all_results.get('monitoring', {}).get('skipped', 0)}
- Duración: {all_results.get('monitoring', {}).get('duration', 0):.2f}s

### 🤖 Tests de DevAgent
- Pasados: {all_results.get('devagent', {}).get('passed', 0)}
- Fallidos: {all_results.get('devagent', {}).get('failed', 0)}
- Saltados: {all_results.get('devagent', {}).get('skipped', 0)}
- Duración: {all_results.get('devagent', {}).get('duration', 0):.2f}s

### 🌐 Tests de API
- Pasados: {all_results.get('api', {}).get('passed', 0)}
- Fallidos: {all_results.get('api', {}).get('failed', 0)}
- Saltados: {all_results.get('api', {}).get('skipped', 0)}
- Duración: {all_results.get('api', {}).get('duration', 0):.2f}s

## 🎯 Estado General
"""
        
        if total_failed == 0 and total_errors == 0:
            report += "✅ **TODOS LOS TESTS PASARON** - Sistema listo para producción"
        elif total_failed > 0:
            report += f"⚠️ **{total_failed} TESTS FALLARON** - Revisar antes de producción"
        else:
            report += "❌ **ERRORES ENCONTRADOS** - Sistema no estable"
        
        return report
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Ejecutar todos los tests de integración"""
        print("🚀 Iniciando tests de integración del sistema Karl AI Ecosystem")
        print("=" * 60)
        
        all_results = {}
        
        # Ejecutar tests por categoría
        all_results['monitoring'] = self.run_monitoring_tests()
        all_results['devagent'] = self.run_devagent_tests()
        all_results['system'] = self.run_system_tests()
        all_results['api'] = self.run_api_tests()
        
        # Generar reporte
        report = self.generate_report(all_results)
        print(report)
        
        # Guardar reporte
        report_file = self.project_root / "reports" / "integration_tests.md"
        report_file.parent.mkdir(exist_ok=True)
        report_file.write_text(report)
        
        print(f"\n📄 Reporte guardado en: {report_file}")
        
        return all_results


def main():
    """Función principal"""
    runner = IntegrationTestRunner()
    
    try:
        results = runner.run_all_tests()
        
        # Determinar código de salida
        total_failed = sum(results["failed"] for results in results.values())
        total_errors = sum(results["errors"] for results in results.values())
        
        if total_failed == 0 and total_errors == 0:
            print("\n🎉 ¡Todos los tests de integración pasaron!")
            sys.exit(0)
        else:
            print(f"\n❌ {total_failed} tests fallaron, {total_errors} errores")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Tests interrumpidos por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error ejecutando tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
