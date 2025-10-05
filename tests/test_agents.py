
import asyncio
import logging
import sys
import os
from typing import Dict, Any

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.load_utils import BasicConfig
from src.agent.router_agent import initialize_routing_agent
from src.agent.research_agent import initialize_deep_research_agent
from src.agent.excel_agent import initialize_excel_agent
from src.agent.report_generation_agent import initialize_report_agent


class AgentTester:
    """Test harness for all agents in the project."""

    def __init__(self):
        """Initialize the test harness with all agents."""
        self.config = BasicConfig()
        self.logger = self.config.logger or logging.getLogger(__name__)
        self.agents = {}
        self.test_results = []

    def initialize_agents(self):
        """Initialize all available agents."""
        try:
            # Initialize research agent
            self.agents['research'] = initialize_deep_research_agent(self.config)

            # Initialize excel agent
            self.agents['excel'] = initialize_excel_agent(self.config)

            # Initialize router agent
            self.agents['router'] = initialize_routing_agent(self.config)

            # Initialize report agent
            self.agents['report'] = initialize_report_agent(self.config)

            self.logger.info("All agents initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
            raise


    async def test_research_agent(self) -> Dict[str, Any]:
        """Test the research agent with web search queries."""
        self.logger.info("Testing Research Agent...")

        test_queries = [
            "What are the latest developments in artificial intelligence?",
        ]

        results = []
        for query in test_queries:
            try:
                result = await self.agents['research'].run(query)
                results.append({
                    'query': query,
                    'success': True,
                    'output': str(result.output)[:200] + "..." if len(str(result.output)) > 200 else str(result.output)
                })
                self.logger.info(f"Research Agent query successful: {query[:50]}...")
            except Exception as e:
                results.append({
                    'query': query,
                    'success': False,
                    'error': str(e)
                })
                self.logger.error(f"Research Agent query failed: {query[:50]}... - {e}")

        return {
            'agent': 'research',
            'total_tests': len(test_queries),
            'successful_tests': len([r for r in results if r['success']]),
            'results': results
        }

    async def test_excel_agent(self) -> Dict[str, Any]:
        """Test the Excel agent with spreadsheet-related queries."""
        self.logger.info("Testing Excel Agent...")

        test_queries = [
            "How do I create a pivot table in Excel?",
        ]

        results = []
        for query in test_queries:
            try:
                result = await self.agents['excel'].run(query)
                results.append({
                    'query': query,
                    'success': True,
                    'output': str(result.output)[:300] + "..." if len(str(result.output)) > 300 else str(result.output)
                })
                self.logger.info(f"Excel Agent query successful: {query[:50]}...")
            except Exception as e:
                results.append({
                    'query': query,
                    'success': False,
                    'error': str(e)
                })
                self.logger.error(f"Excel Agent query failed: {query[:50]}... - {e}")

        return {
            'agent': 'excel',
            'total_tests': len(test_queries),
            'successful_tests': len([r for r in results if r['success']]),
            'results': results
        }

    async def test_router_agent(self) -> Dict[str, Any]:
        """Test the router agent which coordinates between research and Excel agents."""
        self.logger.info("Testing Router Agent...")

        test_queries = [
            "What is machine learning?",  # Should route to research
            "How can I create charts in Excel?"  # Should route to Excel
        ]

        results = []
        for query in test_queries:
            try:
                result = await self.agents['router'].run(query)
                results.append({
                    'query': query,
                    'success': True,
                    'output': str(result.output)[:200] + "..." if len(str(result.output)) > 200 else str(result.output)
                })
                self.logger.info(f"Router Agent query successful: {query[:50]}...")
            except Exception as e:
                results.append({
                    'query': query,
                    'success': False,
                    'error': str(e)
                })
                self.logger.error(f"Router Agent query failed: {query[:50]}... - {e}")

        return {
            'agent': 'router',
            'total_tests': len(test_queries),
            'successful_tests': len([r for r in results if r['success']]),
            'results': results
        }

    async def test_report_agent(self) -> Dict[str, Any]:
        """Test the report generation agent."""
        self.logger.info("Testing Report Generation Agent...")

        test_queries = [
            "Create a summary report about renewable energy trends.",
        ]

        results = []
        for query in test_queries:
            try:
                result = await self.agents['report'].run(query)
                results.append({
                    'query': query,
                    'success': True,
                    'output': str(result.output)[:300] + "..." if len(str(result.output)) > 300 else str(result.output)
                })
                self.logger.info(f"Report Agent query successful: {query[:50]}...")
            except Exception as e:
                results.append({
                    'query': query,
                    'success': False,
                    'error': str(e)
                })
                self.logger.error(f"Report Agent query failed: {query[:50]}... - {e}")

        return {
            'agent': 'report',
            'total_tests': len(test_queries),
            'successful_tests': len([r for r in results if r['success']]),
            'results': results
        }

    def print_test_results(self, results: Dict[str, Any]):
        """Print formatted test results."""
        print(f"\n{'='*60}")
        print(f"TEST RESULTS FOR {results['agent'].upper()} AGENT")
        print(f"{'='*60}")
        print(f"Total Tests: {results['total_tests']}")
        print(f"Successful Tests: {results['successful_tests']}")
        print(f"Success Rate: {(results['successful_tests']/results['total_tests']*100):.1f}%")
        print()

        for i, result in enumerate(results['results'], 1):
            print(f"Test {i}: {result['query'][:60]}...")
            if result['success']:
                print(f"  ✓ SUCCESS: {result['output']}")
            else:
                print(f"  ✗ FAILED: {result['error']}")
            print()

    async def run_all_tests(self):
        """Run all agent tests and collect results."""
        print("Starting comprehensive agent testing...")
        print("=" * 60)

        # Test each agent
        test_methods = [
            ('research', self.test_research_agent),
            ('excel', self.test_excel_agent),
            ('router', self.test_router_agent),
            ('report', self.test_report_agent)
        ]

        all_results = []

        for agent_name, test_method in test_methods:
            if agent_name in self.agents and self.agents[agent_name] is not None:
                try:
                    result = await test_method()
                    all_results.append(result)
                    self.print_test_results(result)
                except Exception as e:
                    self.logger.error(f"Failed to test {agent_name} agent: {e}")
                    print(f"✗ Failed to test {agent_name} agent: {e}")
            else:
                print(f"⚠ {agent_name} agent not available for testing")

        # Print summary
        self.print_summary(all_results)

    def print_summary(self, all_results: list):
        """Print a summary of all test results."""
        print(f"\n{'='*60}")
        print("FINAL TEST SUMMARY")
        print(f"{'='*60}")

        total_tests = sum(r['total_tests'] for r in all_results)
        total_successful = sum(r['successful_tests'] for r in all_results)

        print(f"Total Tests Run: {total_tests}")
        print(f"Total Successful: {total_successful}")
        print(f"Overall Success Rate: {(total_successful/total_tests*100):.1f}%")

        print("\nAgent Breakdown:")
        for result in all_results:
            success_rate = (result['successful_tests'] / result['total_tests'] * 100)
            print(f"  {result['agent'].upper()}: {success_rate:.1f}% ({result['successful_tests']}/{result['total_tests']})")


async def main():
    """Main function to run all tests."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    tester = AgentTester()

    try:
        # Initialize all agents
        print("Initializing agents...")
        tester.initialize_agents()

        # Run all tests
        await tester.run_all_tests()

        print("\n✓ All tests completed!")

    except Exception as e:
        print(f"✗ Test suite failed: {e}")
        logging.error(f"Test suite error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
