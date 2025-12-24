# docker_ops/ai_explainer.py
from typing import Dict, List, Optional
import json

class AIExplainer:
    """Explique les problèmes Docker avec des suggestions intelligentes"""
    
    def __init__(self, llm_client=None):
        # Si vous avez un client LLM, utilisez-le. Sinon, utilisez des règles
        self.llm_client = llm_client
        self.knowledge_base = {
            'CPU': {
                'symptoms': ['High CPU usage', 'Slow performance', 'Lagging'],
                'causes': [
                    'Application bugs or infinite loops',
                    'Insufficient CPU limits',
                    'Background processes consuming resources',
                    'DDoS attack or high traffic'
                ],
                'solutions': [
                    'Check application logs for errors',
                    'Increase CPU limits in Docker: docker update --cpus=2 <container>',
                    'Optimize application code',
                    'Scale horizontally with more containers',
                    'Use monitoring tools to identify the process'
                ]
            },
            'MEMORY': {
                'symptoms': ['High memory usage', 'Out of Memory errors', 'Container crashes'],
                'causes': [
                    'Memory leaks in application',
                    'Insufficient memory limits',
                    'Cache buildup',
                    'Large dataset processing'
                ],
                'solutions': [
                    'Increase memory limit: docker update -m 1g <container>',
                    'Add swap space if not available',
                    'Optimize application memory usage',
                    'Implement garbage collection',
                    'Monitor with: docker stats'
                ]
            },
            'RESTARTS': {
                'symptoms': ['Container restarting frequently', 'Intermittent downtime'],
                'causes': [
                    'Application crashing on errors',
                    'Health check failures',
                    'Resource exhaustion (OOM)',
                    'Docker daemon issues'
                ],
                'solutions': [
                    'Check container logs: docker logs <container>',
                    'Review application error handling',
                    'Adjust restart policy: docker update --restart=on-failure:5 <container>',
                    'Increase resource limits',
                    'Check Docker daemon logs'
                ]
            },
            'STATUS': {
                'symptoms': ['Container not running', 'Exited state', 'Failed to start'],
                'causes': [
                    'Application startup error',
                    'Missing dependencies',
                    'Port conflicts',
                    'Permission issues',
                    'Incorrect command or entrypoint'
                ],
                'solutions': [
                    'Check startup logs: docker logs <container>',
                    'Verify port mappings are not conflicting',
                    'Check volume mounts and permissions',
                    'Test with simpler configuration',
                    'Review Dockerfile and entrypoint'
                ]
            },
            'PIDS': {
                'symptoms': ['High process count', 'Slow fork operations', 'Resource exhaustion'],
                'causes': [
                    'Fork bombs or recursive process creation',
                    'Application spawning too many threads',
                    'Misconfigured process limits'
                ],
                'solutions': [
                    'Set process limits: docker update --pids-limit=100 <container>',
                    'Review application process management',
                    'Check for infinite loops creating processes',
                    'Monitor with: docker top <container>'
                ]
            },
            'OOM': {
                'symptoms': ['Container killed by OOM', 'Sudden termination', 'Memory spikes'],
                'causes': [
                    'Memory leak',
                    'Insufficient memory limit',
                    'Memory-intensive operations',
                    'Cache not being released'
                ],
                'solutions': [
                    'Increase memory limits immediately',
                    'Add swap space',
                    'Implement memory monitoring',
                    'Optimize application memory usage',
                    'Use memory profiling tools'
                ]
            }
        }
    
    def explain_anomaly(self, anomaly: Dict, container_info: Dict) -> str:
        """Génère une explication pour une anomalie"""
        anomaly_type = anomaly.get('type')
        
        if anomaly_type not in self.knowledge_base:
            return self._generate_generic_explanation(anomaly, container_info)
        
        kb = self.knowledge_base[anomaly_type]
        
        explanation = f"##  **AI Analysis - {anomaly_type} Issue**\n\n"
        
        # Description
        explanation += "###  **Description**\n"
        explanation += f"{anomaly.get('message', 'No description available')}\n\n"
        
        # Symptoms
        explanation += "###  **Common Symptoms**\n"
        for symptom in kb['symptoms']:
            explanation += f"- {symptom}\n"
        explanation += "\n"
        
        # Possible Causes
        explanation += "###  **Possible Causes**\n"
        for i, cause in enumerate(kb['causes'], 1):
            explanation += f"{i}. {cause}\n"
        explanation += "\n"
        
        # Recommended Solutions
        explanation += "###  **Recommended Solutions**\n"
        for i, solution in enumerate(kb['solutions'], 1):
            explanation += f"{i}. {solution}\n"
        explanation += "\n"
        
        # Container-specific advice
        explanation += self._generate_container_specific_advice(anomaly, container_info)
        
        return explanation
    
    def explain_logs(self, logs: str, error_patterns: List[str]) -> str:
        """Analyse les logs et fournit des explications"""
        # Analyse simple basée sur des motifs
        analysis = "## **Log Analysis Summary**\n\n"
        
        # Compter les erreurs
        error_count = len(error_patterns)
        
        analysis += f"**Errors detected:** {error_count}\n\n"
        
        if error_count == 0:
            analysis += "✅ No significant errors found in logs.\n"
            return analysis
        
        # Catégoriser les erreurs
        categories = self._categorize_errors(error_patterns)
        
        analysis += "###  **Error Categories**\n"
        for category, count in categories.items():
            analysis += f"- {category}: {count} errors\n"
        analysis += "\n"
        
        # Conseils par catégorie
        analysis += "###  **Recommendations**\n"
        
        if 'Connection' in categories:
            analysis += "1. **Connection Issues**: Check network connectivity and firewall rules\n"
        
        if 'Permission' in categories:
            analysis += "2. **Permission Issues**: Verify file permissions and user access\n"
        
        if 'Resource' in categories:
            analysis += "3. **Resource Issues**: Check CPU, memory, and disk usage\n"
        
        if 'Application' in categories:
            analysis += "4. **Application Errors**: Review application code and configuration\n"
        
        analysis += "\n"
        analysis += "###  **Next Steps**\n"
        analysis += "1. Review detailed logs with: `docker logs --tail=100 <container>`\n"
        analysis += "2. Check container health: `docker inspect <container>`\n"
        analysis += "3. Monitor resources: `docker stats <container>`\n"
        
        return analysis
    
    def _categorize_errors(self, error_patterns: List[str]) -> Dict:
        """Catégorise les erreurs par type"""
        categories = {}
        
        for pattern in error_patterns:
            pattern_lower = pattern.lower()
            
            if any(word in pattern_lower for word in ['connect', 'refused', 'timeout', 'network']):
                category = 'Connection'
            elif any(word in pattern_lower for word in ['permission', 'denied', 'access', 'forbidden']):
                category = 'Permission'
            elif any(word in pattern_lower for word in ['memory', 'cpu', 'disk', 'resource', 'oom']):
                category = 'Resource'
            elif any(word in pattern_lower for word in ['error', 'exception', 'fail', 'crash']):
                category = 'Application'
            else:
                category = 'Other'
            
            categories[category] = categories.get(category, 0) + 1
        
        return categories
    
    def _generate_generic_explanation(self, anomaly: Dict, container_info: Dict) -> str:
        """Génère une explication générique pour les types inconnus"""
        explanation = f"##  **Issue Detected**\n\n"
        explanation += f"**Type:** {anomaly.get('type', 'Unknown')}\n"
        explanation += f"**Level:** {anomaly.get('level', 'Unknown')}\n"
        explanation += f"**Message:** {anomaly.get('message', 'No details')}\n\n"
        
        explanation += "###  **General Troubleshooting**\n"
        explanation += "1. Check container logs: `docker logs <container>`\n"
        explanation += "2. Inspect container state: `docker inspect <container>`\n"
        explanation += "3. Monitor resource usage: `docker stats <container>`\n"
        explanation += "4. Restart the container: `docker restart <container>`\n"
        explanation += "5. Check Docker daemon logs\n\n"
        
        explanation += "###  **Additional Resources**\n"
        explanation += "- Docker Documentation: https://docs.docker.com\n"
        explanation += "- Docker Forums: https://forums.docker.com\n"
        
        return explanation
    
    def _generate_container_specific_advice(self, anomaly: Dict, container_info: Dict) -> str:
        """Génère des conseils spécifiques au conteneur"""
        advice = "###  **Container-Specific Advice**\n"
        
        image = container_info.get('image', '').lower()
        
        # Conseils spécifiques à l'image
        if 'nginx' in image:
            advice += "- For nginx: Check configuration with `nginx -t`\n"
            advice += "- Review access and error logs\n"
            advice += "- Verify upstream servers are reachable\n\n"
        
        elif 'redis' in image:
            advice += "- For redis: Check memory usage with `INFO memory`\n"
            advice += "- Monitor connected clients\n"
            advice += "- Consider persistence configuration\n\n"
        
        elif 'postgres' in image:
            advice += "- For postgres: Check logs in `/var/log/postgresql/`\n"
            advice += "- Monitor connections with `pg_stat_activity`\n"
            advice += "- Check disk space for database\n\n"
        
        elif 'node' in image or 'python' in image or 'java' in image:
            advice += "- For applications: Review application logs\n"
            advice += "- Check dependencies and environment variables\n"
            advice += "- Monitor garbage collection and memory usage\n\n"
        
        else:
            advice += "- Review application-specific documentation\n"
            advice += "- Check for updates or patches\n"
            advice += "- Consult the image's official documentation\n\n"
        
        return advice
    
    def generate_health_report(self, container_name: str, metrics: Dict, anomalies: List[Dict]) -> str:
        """Génère un rapport de santé complet"""
        report = f"##  **Health Report: {container_name}**\n\n"
        
        # Métriques actuelles
        report += "###  **Current Metrics**\n"
        report += f"- CPU Usage: {metrics.get('cpu_percent', 0)}%\n"
        report += f"- Memory Usage: {metrics.get('memory_percent', 0)}%\n"
        report += f"- Processes: {metrics.get('pids', 0)}\n\n"
        
        # Évaluation
        if not anomalies:
            report += "### ✅ **Status: HEALTHY**\n"
            report += "No issues detected. Container is running optimally.\n\n"
        else:
            critical_count = sum(1 for a in anomalies if a.get('level') == 'CRITICAL')
            warning_count = sum(1 for a in anomalies if a.get('level') == 'WARNING')
            
            if critical_count > 0:
                report += f"### 🔴 **Status: CRITICAL** ({critical_count} critical issues)\n"
            elif warning_count > 0:
                report += f"### 🟡 **Status: WARNING** ({warning_count} warnings)\n"
            
            report += f"Total issues detected: {len(anomalies)}\n\n"
            
            # Explications pour chaque anomalie
            report += "###  **Issue Details**\n"
            for i, anomaly in enumerate(anomalies, 1):
                report += f"**Issue {i}: {anomaly.get('type')}**\n"
                report += f"- Level: {anomaly.get('level')}\n"
                report += f"- Description: {anomaly.get('message')}\n\n"
        
        # Recommandations
        report += "###  **Recommendations**\n"
        
        cpu = metrics.get('cpu_percent', 0)
        if cpu > 80:
            report += "1. **High CPU**: Consider optimizing code or increasing CPU limits\n"
        elif cpu < 10:
            report += "1. **Low CPU**: Container may be underutilized, consider downsizing\n"
        else:
            report += "1. **CPU**: Usage is within normal range\n"
        
        memory = metrics.get('memory_percent', 0)
        if memory > 80:
            report += "2. **High Memory**: Check for memory leaks or increase limits\n"
        elif memory < 20:
            report += "2. **Low Memory**: Container may be over-provisioned\n"
        else:
            report += "2. **Memory**: Usage is within normal range\n"
        
        report += "\n###  **Immediate Actions**\n"
        report += "1. Monitor trends: `docker stats`\n"
        report += "2. Check logs: `docker logs --tail=50 <container>`\n"
        report += "3. Review configuration: `docker inspect <container>`\n"
        
        return report