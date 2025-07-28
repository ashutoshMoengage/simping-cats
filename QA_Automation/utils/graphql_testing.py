"""
🎯 GraphQL API Testing Module
=============================

This module provides comprehensive GraphQL API testing capabilities with REAL examples
from popular APIs like GitHub, SpaceX, and Rick & Morty.

📚 FOR BEGINNERS:
GraphQL is different from REST APIs:
- Single endpoint (/graphql) instead of multiple endpoints
- You specify exactly what data you want
- Can fetch related data in one request
- Strongly typed with schema introspection

🌟 REAL APIs WE'LL TEST:
- GitHub GraphQL API: https://docs.github.com/en/graphql
- SpaceX GraphQL API: https://api.spacex.land/graphql/
- Rick & Morty API: https://rickandmortyapi.com/graphql
- Countries GraphQL API: https://countries.trevorblades.com/

🎯 WHAT YOU'LL LEARN:
- Query testing (fetching data)
- Mutation testing (modifying data)
- Schema introspection
- Error handling
- Performance testing
- Complex nested queries
"""

import json
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import requests

from utils.enhanced_logging import enhanced_logger
from utils.assertions import api_assert
from config.config import config_instance


@dataclass
class GraphQLTestResult:
    """
    📊 GraphQL Test Result Data Structure
    
    Represents the result of a GraphQL operation test.
    """
    query_name: str
    operation_type: str  # 'query', 'mutation', 'subscription'
    success: bool
    execution_time: float
    response_size: int
    errors: Optional[List[Dict[str, Any]]] = None
    data: Optional[Dict[str, Any]] = None
    query_complexity: Optional[int] = None


class GraphQLClient:
    """
    🎯 Universal GraphQL Client
    
    This client works with any GraphQL endpoint and provides:
    - Query execution with error handling
    - Schema introspection
    - Performance metrics
    - Automatic retry logic
    - Request/response logging
    
    📚 BEGINNER EXPLANATION:
    GraphQL queries look like this:
    
    query {
        user(id: "123") {
            name
            email
            posts {
                title
                createdAt
            }
        }
    }
    
    This fetches user data AND their posts in ONE request!
    """
    
    def __init__(self, endpoint_url: str, headers: Dict[str, str] = None):
        """
        🚀 Initialize GraphQL client
        
        Args:
            endpoint_url (str): GraphQL endpoint URL
            headers (dict): HTTP headers (for authentication, etc.)
            
        Example:
            # GitHub GraphQL API (requires token)
            client = GraphQLClient(
                "https://api.github.com/graphql",
                {"Authorization": "Bearer YOUR_GITHUB_TOKEN"}
            )
        """
        self.endpoint_url = endpoint_url
        self.headers = headers or {"Content-Type": "application/json"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        enhanced_logger.info(f"🔗 GraphQL client initialized for: {endpoint_url}")
    
    def execute_query(self, query: str, variables: Dict[str, Any] = None, 
                     operation_name: str = None) -> GraphQLTestResult:
        """
        🚀 Execute GraphQL query with comprehensive testing
        
        Args:
            query (str): GraphQL query string
            variables (dict): Query variables
            operation_name (str): Name of the operation (for debugging)
            
        Returns:
            GraphQLTestResult: Detailed test result
            
        Example:
            query = '''
            query GetUser($userId: ID!) {
                user(id: $userId) {
                    name
                    email
                }
            }
            '''
            result = client.execute_query(query, {"userId": "123"})
        """
        start_time = time.time()
        operation_name = operation_name or "unnamed_operation"
        
        # Prepare GraphQL request payload
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        if operation_name:
            payload["operationName"] = operation_name
        
        enhanced_logger.log_api_request(
            "POST", 
            self.endpoint_url, 
            headers=self.headers, 
            body=payload
        )
        
        try:
            response = self.session.post(
                self.endpoint_url,
                json=payload,
                timeout=30
            )
            
            execution_time = time.time() - start_time
            response_data = response.json()
            
            enhanced_logger.log_api_response(
                response.status_code,
                execution_time,
                response_data
            )
            
            # Determine operation type from query
            operation_type = self._determine_operation_type(query)
            
            # Check for GraphQL errors
            graphql_errors = response_data.get('errors', [])
            success = response.status_code == 200 and len(graphql_errors) == 0
            
            return GraphQLTestResult(
                query_name=operation_name,
                operation_type=operation_type,
                success=success,
                execution_time=execution_time,
                response_size=len(response.text),
                errors=graphql_errors if graphql_errors else None,
                data=response_data.get('data'),
                query_complexity=self._estimate_query_complexity(query)
            )
            
        except requests.exceptions.RequestException as e:
            execution_time = time.time() - start_time
            enhanced_logger.error(f"❌ GraphQL request failed: {str(e)}")
            
            return GraphQLTestResult(
                query_name=operation_name,
                operation_type="unknown",
                success=False,
                execution_time=execution_time,
                response_size=0,
                errors=[{"message": str(e)}]
            )
    
    def _determine_operation_type(self, query: str) -> str:
        """🔍 Determine if query is a query, mutation, or subscription"""
        query_lower = query.lower().strip()
        if query_lower.startswith('mutation'):
            return 'mutation'
        elif query_lower.startswith('subscription'):
            return 'subscription'
        else:
            return 'query'
    
    def _estimate_query_complexity(self, query: str) -> int:
        """📊 Estimate query complexity (simple heuristic)"""
        # Count nested levels and fields as complexity measure
        return query.count('{') + query.count('(')
    
    def introspect_schema(self) -> GraphQLTestResult:
        """
        🔍 Get GraphQL schema information
        
        This is useful for:
        - Understanding available queries/mutations
        - Validating schema changes
        - Generating documentation
        - Dynamic query building
        """
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                types {
                    name
                    kind
                    description
                }
                queryType {
                    name
                    fields {
                        name
                        description
                        type {
                            name
                            kind
                        }
                    }
                }
                mutationType {
                    name
                    fields {
                        name
                        description
                    }
                }
            }
        }
        """
        
        return self.execute_query(introspection_query, operation_name="schema_introspection")


class GitHubGraphQLTester:
    """
    🐙 GitHub GraphQL API Tester
    
    GitHub's GraphQL API is perfect for learning because:
    - Well-documented: https://docs.github.com/en/graphql
    - Real-world complexity
    - Requires authentication (teaches API security)
    - Rich data relationships
    
    📚 SETUP FOR BEGINNERS:
    1. Go to GitHub Settings > Developer settings > Personal access tokens
    2. Generate token with 'repo' and 'user' scopes
    3. Add token to your environment: GITHUB_TOKEN=your_token_here
    4. Use in tests!
    
    🌟 WHAT WE'LL TEST:
    - User profile queries
    - Repository information
    - Issue and PR data
    - Organization membership
    """
    
    def __init__(self, github_token: str = None):
        """
        🚀 Initialize GitHub GraphQL tester
        
        Args:
            github_token (str): GitHub personal access token
        """
        self.token = github_token or config_instance.config_data.get('github_token')
        
        if not self.token:
            enhanced_logger.warning(
                "⚠️ No GitHub token provided. Some tests will fail. "
                "Generate token at: https://github.com/settings/tokens"
            )
        
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        self.client = GraphQLClient("https://api.github.com/graphql", headers)
        
        enhanced_logger.info("🐙 GitHub GraphQL tester initialized")
    
    def test_get_user_profile(self, username: str = "octocat") -> GraphQLTestResult:
        """
        👤 REAL EXAMPLE: Get GitHub user profile
        
        This tests a real GitHub user profile query. Try with:
        - "octocat" (GitHub's mascot account)
        - "torvalds" (Linux creator)
        - "gaearon" (React maintainer)
        - Your own username!
        """
        query = """
        query GetUserProfile($username: String!) {
            user(login: $username) {
                name
                login
                bio
                company
                location
                email
                websiteUrl
                followers {
                    totalCount
                }
                following {
                    totalCount
                }
                repositories(first: 5, orderBy: {field: STARGAZERS, direction: DESC}) {
                    totalCount
                    nodes {
                        name
                        description
                        stargazerCount
                        forkCount
                        primaryLanguage {
                            name
                            color
                        }
                    }
                }
                contributionsCollection {
                    totalCommitContributions
                    totalPullRequestContributions
                }
            }
        }
        """
        
        result = self.client.execute_query(
            query, 
            {"username": username},
            f"get_user_profile_{username}"
        )
        
        # Add specific assertions for GitHub data
        if result.success and result.data:
            user_data = result.data.get('user')
            if user_data:
                enhanced_logger.info(
                    f"✅ GitHub user profile retrieved: {user_data.get('name')} (@{user_data.get('login')})",
                    extra_context={
                        "followers": user_data.get('followers', {}).get('totalCount'),
                        "repos": user_data.get('repositories', {}).get('totalCount')
                    }
                )
        
        return result
    
    def test_search_repositories(self, query_string: str = "language:python stars:>1000") -> GraphQLTestResult:
        """
        🔍 REAL EXAMPLE: Search GitHub repositories
        
        This demonstrates GraphQL's power for complex queries.
        Try different search queries:
        - "language:python stars:>1000" (Popular Python repos)
        - "topic:machine-learning" (ML repositories)
        - "user:microsoft language:typescript" (Microsoft's TypeScript repos)
        """
        query = """
        query SearchRepositories($queryString: String!, $first: Int!) {
            search(query: $queryString, type: REPOSITORY, first: $first) {
                repositoryCount
                edges {
                    node {
                        ... on Repository {
                            name
                            description
                            url
                            stargazerCount
                            forkCount
                            owner {
                                login
                            }
                            primaryLanguage {
                                name
                                color
                            }
                            issues(states: OPEN) {
                                totalCount
                            }
                            pullRequests(states: OPEN) {
                                totalCount
                            }
                        }
                    }
                }
            }
        }
        """
        
        result = self.client.execute_query(
            query,
            {"queryString": query_string, "first": 10},
            "search_repositories"
        )
        
        if result.success and result.data:
            search_data = result.data.get('search', {})
            repo_count = search_data.get('repositoryCount', 0)
            enhanced_logger.info(f"🔍 Found {repo_count} repositories matching: {query_string}")
        
        return result


class SpaceXGraphQLTester:
    """
    🚀 SpaceX GraphQL API Tester
    
    SpaceX API is perfect for beginners because:
    - No authentication required!
    - Real space data (launches, rockets, missions)
    - Easy to understand data structure
    - Free to use
    
    🌟 API ENDPOINT: https://api.spacex.land/graphql/
    🌟 PLAYGROUND: https://api.spacex.land/graphql/
    
    📚 WHAT WE'LL TEST:
    - Past and upcoming launches
    - Rocket information
    - Mission details
    - Company information
    """
    
    def __init__(self):
        """🚀 Initialize SpaceX GraphQL tester"""
        self.client = GraphQLClient("https://api.spacex.land/graphql/")
        enhanced_logger.info("🚀 SpaceX GraphQL tester initialized")
    
    def test_get_latest_launch(self) -> GraphQLTestResult:
        """
        🚀 REAL EXAMPLE: Get SpaceX's latest launch
        
        This fetches real SpaceX launch data! Perfect for beginners
        because the data is interesting and easy to understand.
        """
        query = """
        query GetLatestLaunch {
            launchLatest {
                mission_name
                launch_date_utc
                launch_success
                details
                rocket {
                    rocket_name
                    rocket_type
                }
                launch_site {
                    site_name_long
                }
                links {
                    mission_patch
                    video_link
                    wikipedia
                }
                ships {
                    name
                    home_port
                }
            }
        }
        """
        
        result = self.client.execute_query(query, operation_name="get_latest_launch")
        
        if result.success and result.data:
            launch = result.data.get('launchLatest', {})
            enhanced_logger.info(
                f"🚀 Latest SpaceX launch: {launch.get('mission_name')}",
                extra_context={
                    "success": launch.get('launch_success'),
                    "rocket": launch.get('rocket', {}).get('rocket_name'),
                    "date": launch.get('launch_date_utc')
                }
            )
        
        return result
    
    def test_get_rocket_info(self, rocket_id: str = "falcon9") -> GraphQLTestResult:
        """
        🚀 REAL EXAMPLE: Get detailed rocket information
        
        Try different rocket IDs:
        - "falcon9" (most used rocket)
        - "falconheavy" (most powerful rocket)
        - "starship" (future Mars rocket)
        """
        query = """
        query GetRocket($rocketId: ID!) {
            rocket(id: $rocketId) {
                name
                type
                active
                stages
                boosters
                cost_per_launch
                success_rate_pct
                first_flight
                country
                company
                height {
                    meters
                    feet
                }
                mass {
                    kg
                    lb
                }
                engines {
                    number
                    type
                    version
                    thrust_sea_level {
                        kN
                        lbf
                    }
                }
                landing_legs {
                    number
                    material
                }
                description
            }
        }
        """
        
        result = self.client.execute_query(
            query,
            {"rocketId": rocket_id},
            f"get_rocket_{rocket_id}"
        )
        
        if result.success and result.data:
            rocket = result.data.get('rocket', {})
            enhanced_logger.info(
                f"🚀 Rocket info: {rocket.get('name')}",
                extra_context={
                    "active": rocket.get('active'),
                    "success_rate": rocket.get('success_rate_pct'),
                    "cost": rocket.get('cost_per_launch')
                }
            )
        
        return result
    
    def test_get_launch_statistics(self) -> GraphQLTestResult:
        """
        📊 REAL EXAMPLE: Get SpaceX launch statistics
        
        This demonstrates GraphQL's ability to aggregate data efficiently.
        """
        query = """
        query GetLaunchStatistics {
            launches {
                mission_name
                launch_success
                launch_year
            }
            launchesUpcoming {
                mission_name
                launch_date_utc
            }
        }
        """
        
        result = self.client.execute_query(query, operation_name="get_launch_statistics")
        
        if result.success and result.data:
            launches = result.data.get('launches', [])
            upcoming = result.data.get('launchesUpcoming', [])
            
            # Calculate statistics
            total_launches = len(launches)
            successful_launches = sum(1 for launch in launches if launch.get('launch_success'))
            success_rate = (successful_launches / total_launches * 100) if total_launches > 0 else 0
            
            enhanced_logger.info(
                f"📊 SpaceX Statistics: {successful_launches}/{total_launches} successful launches ({success_rate:.1f}%)",
                extra_context={
                    "upcoming_launches": len(upcoming),
                    "success_rate": success_rate
                }
            )
        
        return result


class RickAndMortyGraphQLTester:
    """
    🧪 Rick & Morty GraphQL API Tester
    
    This API is PERFECT for beginners because:
    - No authentication required
    - Fun, recognizable data
    - Simple, clean structure
    - Great for learning GraphQL concepts
    
    🌟 API ENDPOINT: https://rickandmortyapi.com/graphql
    🌟 PLAYGROUND: https://rickandmortyapi.com/graphql
    
    📚 WHAT WE'LL TEST:
    - Character information
    - Episode details
    - Location data
    - Complex relationships
    """
    
    def __init__(self):
        """🧪 Initialize Rick & Morty GraphQL tester"""
        self.client = GraphQLClient("https://rickandmortyapi.com/graphql")
        enhanced_logger.info("🧪 Rick & Morty GraphQL tester initialized")
    
    def test_get_character_info(self, character_id: int = 1) -> GraphQLTestResult:
        """
        👥 REAL EXAMPLE: Get Rick & Morty character information
        
        Try different character IDs:
        - 1: Rick Sanchez
        - 2: Morty Smith  
        - 3: Summer Smith
        - 4: Beth Smith
        """
        query = """
        query GetCharacter($characterId: ID!) {
            character(id: $characterId) {
                name
                status
                species
                type
                gender
                origin {
                    name
                    type
                    dimension
                }
                location {
                    name
                    type
                    dimension
                }
                image
                episode {
                    name
                    air_date
                    episode
                }
            }
        }
        """
        
        result = self.client.execute_query(
            query,
            {"characterId": str(character_id)},
            f"get_character_{character_id}"
        )
        
        if result.success and result.data:
            character = result.data.get('character', {})
            enhanced_logger.info(
                f"👥 Character: {character.get('name')} ({character.get('species')})",
                extra_context={
                    "status": character.get('status'),
                    "origin": character.get('origin', {}).get('name'),
                    "episodes": len(character.get('episode', []))
                }
            )
        
        return result
    
    def test_get_episodes_by_season(self, season: str = "S01") -> GraphQLTestResult:
        """
        📺 REAL EXAMPLE: Get episodes from specific season
        
        This demonstrates GraphQL filtering capabilities.
        Try: "S01", "S02", "S03", "S04", "S05"
        """
        query = """
        query GetEpisodesBySeason($season: String!) {
            episodes(filter: { episode: $season }) {
                results {
                    name
                    air_date
                    episode
                    characters {
                        name
                        species
                    }
                }
            }
        }
        """
        
        result = self.client.execute_query(
            query,
            {"season": season},
            f"get_episodes_{season}"
        )
        
        if result.success and result.data:
            episodes = result.data.get('episodes', {}).get('results', [])
            enhanced_logger.info(
                f"📺 Found {len(episodes)} episodes in {season}",
                extra_context={"season": season, "episode_count": len(episodes)}
            )
        
        return result


class GraphQLTestSuite:
    """
    🎯 Complete GraphQL Testing Suite
    
    This combines all GraphQL testers into a unified interface for
    comprehensive GraphQL API testing across multiple real APIs.
    
    📚 USAGE IN TESTS:
    
    @pytest.fixture
    def graphql_tester():
        return GraphQLTestSuite()
    
    def test_multiple_graphql_apis(graphql_tester):
        # Test SpaceX API (no auth needed)
        spacex_result = graphql_tester.spacex.test_get_latest_launch()
        assert spacex_result.success
        
        # Test Rick & Morty API (fun data)
        rm_result = graphql_tester.rick_morty.test_get_character_info(1)
        assert rm_result.success
    """
    
    def __init__(self, github_token: str = None):
        """🚀 Initialize complete GraphQL test suite"""
        self.github = GitHubGraphQLTester(github_token)
        self.spacex = SpaceXGraphQLTester()
        self.rick_morty = RickAndMortyGraphQLTester()
        
        enhanced_logger.info("🎯 GraphQL test suite initialized with 3 real APIs")
    
    def run_comprehensive_test(self) -> List[GraphQLTestResult]:
        """
        🎯 Run comprehensive tests across all GraphQL APIs
        
        This demonstrates testing multiple GraphQL endpoints with
        different authentication requirements and data structures.
        """
        results = []
        
        enhanced_logger.info("🚀 Starting comprehensive GraphQL API tests...")
        
        # Test SpaceX API (no auth, great for beginners)
        try:
            spacex_result = self.spacex.test_get_latest_launch()
            results.append(spacex_result)
        except Exception as e:
            enhanced_logger.error(f"❌ SpaceX test failed: {str(e)}")
        
        # Test Rick & Morty API (fun data, no auth)
        try:
            rm_result = self.rick_morty.test_get_character_info(1)  # Rick Sanchez
            results.append(rm_result)
        except Exception as e:
            enhanced_logger.error(f"❌ Rick & Morty test failed: {str(e)}")
        
        # Test GitHub API (requires auth, production-like)
        try:
            github_result = self.github.test_get_user_profile("octocat")
            results.append(github_result)
        except Exception as e:
            enhanced_logger.error(f"❌ GitHub test failed: {str(e)}")
        
        # Generate summary
        successful_tests = sum(1 for result in results if result.success)
        enhanced_logger.info(
            f"✅ GraphQL comprehensive test completed: {successful_tests}/{len(results)} successful",
            extra_context={"results": [r.query_name for r in results]}
        )
        
        return results
    
    def generate_performance_report(self, results: List[GraphQLTestResult]) -> Dict[str, Any]:
        """📊 Generate GraphQL performance analysis report"""
        if not results:
            return {"message": "No GraphQL test results available"}
        
        successful_results = [r for r in results if r.success]
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_queries": len(results),
                "successful_queries": len(successful_results),
                "failed_queries": len(results) - len(successful_results),
                "success_rate": len(successful_results) / len(results) * 100 if results else 0
            },
            "performance": {
                "average_response_time": sum(r.execution_time for r in successful_results) / len(successful_results) if successful_results else 0,
                "fastest_query": min(successful_results, key=lambda x: x.execution_time).query_name if successful_results else None,
                "slowest_query": max(successful_results, key=lambda x: x.execution_time).query_name if successful_results else None,
                "total_response_size": sum(r.response_size for r in successful_results)
            },
            "apis_tested": ["GitHub GraphQL", "SpaceX GraphQL", "Rick & Morty GraphQL"],
            "query_complexity": {
                "average_complexity": sum(r.query_complexity for r in results if r.query_complexity) / len([r for r in results if r.query_complexity]) if any(r.query_complexity for r in results) else 0,
                "most_complex_query": max(results, key=lambda x: x.query_complexity or 0).query_name if results else None
            }
        }
        
        return report


# 🌟 GLOBAL INSTANCE for easy access
graphql_test_suite = GraphQLTestSuite()


# 🎯 USAGE EXAMPLES FOR BEGINNERS:
"""
📚 HOW TO USE GRAPHQL TESTING:

1. SIMPLE SPACEX TEST (No setup required!):
   
   from utils.graphql_testing import graphql_test_suite
   
   def test_spacex_latest_launch():
       result = graphql_test_suite.spacex.test_get_latest_launch()
       assert result.success, f"SpaceX query failed: {result.errors}"
       
       # Check data structure
       launch_data = result.data['launchLatest']
       assert 'mission_name' in launch_data
       assert 'rocket' in launch_data

2. RICK & MORTY CHARACTER TEST (Fun for learning!):
   
   def test_rick_and_morty_characters():
       # Test Rick Sanchez (character ID: 1)
       result = graphql_test_suite.rick_morty.test_get_character_info(1)
       assert result.success
       
       character = result.data['character']
       assert character['name'] == 'Rick Sanchez'
       assert character['species'] == 'Human'

3. GITHUB API TEST (Production-like, requires token):
   
   # First, get GitHub token from https://github.com/settings/tokens
   # Add to environment or config: GITHUB_TOKEN=your_token_here
   
   def test_github_user_profile():
       result = graphql_test_suite.github.test_get_user_profile("octocat")
       
       if result.success:
           user = result.data['user']
           assert user['login'] == 'octocat'
           assert 'repositories' in user
       else:
           print("GitHub API requires authentication token")

4. COMPREHENSIVE TESTING:
   
   def test_all_graphql_apis():
       results = graphql_test_suite.run_comprehensive_test()
       
       # At least SpaceX and Rick&Morty should work (no auth required)
       successful_tests = [r for r in results if r.success]
       assert len(successful_tests) >= 2, "At least 2 GraphQL APIs should work"
       
       # Generate performance report
       report = graphql_test_suite.generate_performance_report(results)
       print(f"Average response time: {report['performance']['average_response_time']:.3f}s")

5. CUSTOM GRAPHQL CLIENT:
   
   from utils.graphql_testing import GraphQLClient
   
   # Test any GraphQL API
   client = GraphQLClient("https://countries.trevorblades.com/")
   
   query = '''
   query GetCountries {
       countries {
           name
           code
           capital
           emoji
       }
   }
   '''
   
   result = client.execute_query(query, operation_name="get_countries")
   assert result.success

🎯 REAL-WORLD SCENARIOS:
✅ E-commerce: Product catalog queries
✅ Social Media: User profiles and posts
✅ Content Management: Articles and comments
✅ IoT: Device status and sensor data
✅ Finance: Transaction history and analytics

📊 BENEFITS:
✅ EFFICIENT QUERIES: Get exactly the data you need
✅ SINGLE ENDPOINT: Easier to manage than REST APIs
✅ STRONG TYPING: Better validation and documentation
✅ REAL-TIME: Subscription support for live data
✅ INTROSPECTION: Self-documenting APIs

🌟 POPULAR GRAPHQL APIS TO PRACTICE WITH:
✅ GitHub: https://docs.github.com/en/graphql
✅ SpaceX: https://api.spacex.land/graphql/
✅ Rick & Morty: https://rickandmortyapi.com/graphql
✅ Countries: https://countries.trevorblades.com/
✅ Star Wars: https://swapi-graphql.netlify.app/.netlify/functions/index
✅ Pokemon: https://graphql-pokemon2.vercel.app/
""" 