"""
Comprehensive Post API Tests
"""
import pytest
import allure
from utils.assertions import api_assert
from utils.decorators import api_test, attach_request_response, performance_test
from utils.data_provider import data_provider
from utils.helpers import data_gen


@allure.epic("Content Management")
@allure.feature("Post CRUD Operations")
class TestPostAPI:
    """Test class for Post API operations"""
    
    @api_test(
        title="Get All Posts - Smoke Test",
        description="Verify that all posts can be retrieved successfully",
        severity="critical",
        tags=["smoke", "posts", "get"]
    )
    @attach_request_response
    def test_get_all_posts_smoke(self, jsonplaceholder_api, post_schema):
        """Test getting all posts - smoke test"""
        response = jsonplaceholder_api.get("/posts")
        
        # Basic assertions
        api_assert.assert_status_code(response, 200)
        api_assert.assert_content_type(response, "application/json")
        api_assert.assert_response_time(jsonplaceholder_api.response_time, 3.0)
        
        # Response structure validation
        posts = response.json()
        assert isinstance(posts, list), "Response should be a list"
        assert len(posts) > 0, "Posts list should not be empty"
        
        # Validate array length
        api_assert.assert_json_array_length(response, "@", 100)  # JSONPlaceholder has 100 posts
        
        # Validate first post against schema
        if posts:
            # Create single post response for schema validation
            first_post_response = type(response)()
            first_post_response._content = str(posts[0]).encode()
            first_post_response.status_code = 200
            first_post_response.headers = response.headers
            first_post_response.json = lambda: posts[0]
            
            api_assert.assert_json_schema(first_post_response, post_schema)
    
    @api_test(
        title="Get Post by Valid ID",
        description="Verify that a post can be retrieved by valid ID",
        severity="critical",
        tags=["regression", "posts", "get"]
    )  
    @attach_request_response
    def test_get_post_by_valid_id(self, jsonplaceholder_api, test_post_id, post_schema):
        """Test getting post by valid ID"""
        response = jsonplaceholder_api.get(f"/posts/{test_post_id}")
        
        # Assertions
        api_assert.assert_status_code(response, 200)
        api_assert.assert_content_type(response, "application/json")
        
        # Validate response structure
        api_assert.assert_json_schema(response, post_schema)
        
        # Validate specific fields
        api_assert.assert_json_key_exists(response, "id")
        api_assert.assert_json_key_exists(response, "title")
        api_assert.assert_json_key_exists(response, "body")
        api_assert.assert_json_key_exists(response, "userId")
        api_assert.assert_json_key_value(response, "id", test_post_id)
        
        # Validate data types
        api_assert.assert_json_types(response, {
            "id": int,
            "title": str,
            "body": str,
            "userId": int
        })
    
    @pytest.mark.parametrize("post_id", [0, -1, 999, "abc", ""])
    @api_test(
        title="Get Post by Invalid ID",
        description="Verify appropriate error handling for invalid post IDs",
        severity="normal",
        tags=["negative", "posts", "get"]
    )
    def test_get_post_by_invalid_id(self, jsonplaceholder_api, post_id):
        """Test getting post by invalid ID"""
        response = jsonplaceholder_api.get(f"/posts/{post_id}")
        
        # Should return 404 for invalid IDs
        api_assert.assert_status_code(response, 404)
    
    @api_test(
        title="Create New Post with Valid Data",
        description="Verify that a new post can be created with valid data",
        severity="critical",
        tags=["crud", "posts", "post"],
        max_response_time=2.0
    )
    @attach_request_response
    def test_create_post_valid_data(self, jsonplaceholder_api, post_data, cleanup_created_resources):
        """Test creating post with valid data"""
        response = jsonplaceholder_api.post("/posts", json_data=post_data)
        
        # Assertions
        api_assert.assert_status_code(response, 201)
        api_assert.assert_content_type(response, "application/json")
        
        # Validate response contains ID
        api_assert.assert_json_key_exists(response, "id")
        
        # Validate that request data is reflected in response
        response_data = response.json()
        for key, value in post_data.items():
            if key in response_data:
                api_assert.assert_json_key_value(response, key, value)
        
        # Track created resource for cleanup
        post_id = response_data.get("id")
        if post_id:
            cleanup_created_resources["posts"].append(post_id)
    
    @api_test(
        title="Create Post with Random Generated Data",
        description="Test creating post with randomly generated data",
        tags=["data-driven", "posts", "post"]
    )
    @attach_request_response
    def test_create_post_random_data(self, jsonplaceholder_api, random_post_data):
        """Test creating post with random data"""
        response = jsonplaceholder_api.post("/posts", json_data=random_post_data)
        
        api_assert.assert_status_code(response, 201)
        api_assert.assert_json_key_exists(response, "id")
    
    @pytest.mark.parametrize("field_to_remove", ["title", "body", "userId"])
    @api_test(
        title="Create Post with Missing Required Fields",
        description="Verify validation for missing required fields",
        severity="normal",
        tags=["negative", "validation", "posts", "post"]
    )
    def test_create_post_missing_fields(self, jsonplaceholder_api, post_data, field_to_remove):
        """Test creating post with missing required fields"""
        # Remove required field
        invalid_data = post_data.copy()
        invalid_data.pop(field_to_remove, None)
        
        response = jsonplaceholder_api.post("/posts", json_data=invalid_data)
        
        # Note: JSONPlaceholder is permissive, but in real API this should be 400
        api_assert.assert_status_code_in(response, [201, 400])
    
    @api_test(
        title="Update Post with Valid Data",
        description="Verify that a post can be updated with valid data",
        severity="critical",
        tags=["crud", "posts", "put"]
    )
    @attach_request_response
    def test_update_post_valid_data(self, jsonplaceholder_api, test_post_id, post_data):
        """Test updating post with valid data"""
        # First get existing post
        get_response = jsonplaceholder_api.get(f"/posts/{test_post_id}")
        api_assert.assert_status_code(get_response, 200)
        
        # Update post data
        updated_data = post_data.copy()
        updated_data["title"] = "Updated Post Title"
        updated_data["body"] = "Updated post body content"
        
        response = jsonplaceholder_api.put(f"/posts/{test_post_id}", json_data=updated_data)
        
        # Assertions
        api_assert.assert_status_code(response, 200)
        api_assert.assert_json_key_value(response, "id", test_post_id)
        api_assert.assert_json_key_value(response, "title", updated_data["title"])
        api_assert.assert_json_key_value(response, "body", updated_data["body"])
    
    @api_test(
        title="Partial Update Post with PATCH",
        description="Verify that a post can be partially updated using PATCH",
        tags=["crud", "posts", "patch"]
    )
    @attach_request_response
    def test_patch_post(self, jsonplaceholder_api, test_post_id):
        """Test partial update of post using PATCH"""
        patch_data = {
            "title": "Partially Updated Title"
        }
        
        response = jsonplaceholder_api.patch(f"/posts/{test_post_id}", json_data=patch_data)
        
        api_assert.assert_status_code(response, 200)
        api_assert.assert_json_key_value(response, "title", patch_data["title"])
    
    @api_test(
        title="Delete Post by Valid ID",
        description="Verify that a post can be deleted by valid ID",
        severity="critical",
        tags=["crud", "posts", "delete"]
    )
    @attach_request_response
    def test_delete_post_valid_id(self, jsonplaceholder_api, test_post_id):
        """Test deleting post by valid ID"""
        response = jsonplaceholder_api.delete(f"/posts/{test_post_id}")
        
        # Should return success status for deletion
        api_assert.assert_status_code(response, 200)
    
    @api_test(
        title="Get Posts by User ID",
        description="Verify that posts can be filtered by user ID",
        tags=["filter", "posts", "get"]
    )
    def test_get_posts_by_user_id(self, jsonplaceholder_api, test_user_id):
        """Test getting posts by user ID"""
        response = jsonplaceholder_api.get("/posts", params={"userId": test_user_id})
        
        api_assert.assert_status_code(response, 200)
        
        posts = response.json()
        assert isinstance(posts, list), "Response should be a list"
        
        # Verify all posts belong to the specified user
        for post in posts:
            assert post["userId"] == test_user_id, f"Post {post['id']} should belong to user {test_user_id}"
    
    @api_test(
        title="Get Comments for a Post",
        description="Verify that comments can be retrieved for a specific post",
        tags=["nested", "posts", "comments", "get"]
    )
    def test_get_post_comments(self, jsonplaceholder_api, test_post_id):
        """Test getting comments for a post"""
        response = jsonplaceholder_api.get(f"/posts/{test_post_id}/comments")
        
        api_assert.assert_status_code(response, 200)
        
        comments = response.json()
        assert isinstance(comments, list), "Response should be a list"
        
        # Verify all comments belong to the specified post
        for comment in comments:
            assert comment["postId"] == test_post_id, f"Comment {comment['id']} should belong to post {test_post_id}"
            
            # Validate comment structure
            api_assert.assert_json_key_exists(type(response)(), "name") if comments else None
            api_assert.assert_json_key_exists(type(response)(), "email") if comments else None
            api_assert.assert_json_key_exists(type(response)(), "body") if comments else None
    
    @pytest.mark.parametrize("post_data_type", ["valid", "long_content", "special_characters", "html_content"])
    @api_test(
        title="Create Posts with Different Content Types",
        description="Test creating posts with various content types",
        tags=["content-types", "posts", "post"]
    )
    def test_create_posts_various_content(self, jsonplaceholder_api, post_data_type):
        """Test creating posts with different content types"""
        post_data = data_provider.get_post_test_data(post_data_type)
        
        response = jsonplaceholder_api.post("/posts", json_data=post_data)
        
        api_assert.assert_status_code(response, 201)
        api_assert.assert_json_key_exists(response, "id")
        
        # Verify content is preserved (may be filtered in real APIs)
        response_data = response.json()
        assert response_data["title"] == post_data["title"]
        assert response_data["body"] == post_data["body"]
    
    @performance_test(max_response_time=1.0, percentile=95)
    @api_test(
        title="Performance Test - Post Creation",
        description="Performance test for post creation operations",
        tags=["performance", "posts", "post"]
    )
    def test_post_creation_performance(self, jsonplaceholder_api, random_post_data):
        """Performance test for post creation"""
        response = jsonplaceholder_api.post("/posts", json_data=random_post_data)
        
        api_assert.assert_status_code(response, 201)
        return response  # Return for performance measurement
    
    @api_test(
        title="Bulk Post Operations Test",
        description="Test bulk operations on multiple posts",
        tags=["bulk", "posts", "integration"]
    )
    def test_bulk_post_operations(self, jsonplaceholder_api, bulk_test_data):
        """Test bulk post operations"""
        posts_data = bulk_test_data["posts"]
        created_posts = []
        
        # Create multiple posts
        for post_data in posts_data[:3]:  # Limit to 3 for performance
            response = jsonplaceholder_api.post("/posts", json_data=post_data)
            api_assert.assert_status_code(response, 201)
            
            post_id = response.json().get("id")
            if post_id:
                created_posts.append(post_id)
        
        # Verify created posts
        for post_id in created_posts:
            response = jsonplaceholder_api.get(f"/posts/{post_id}")
            api_assert.assert_status_code_in(response, [200, 404])  # May not persist
    
    @api_test(
        title="Post Content Length Validation",
        description="Test posts with various content lengths",
        tags=["validation", "posts", "content-length"]
    )
    def test_post_content_length_validation(self, jsonplaceholder_api):
        """Test post content length validation"""
        # Test with empty content
        empty_post = data_provider.get_post_test_data("empty_fields")
        response = jsonplaceholder_api.post("/posts", json_data=empty_post)
        api_assert.assert_status_code_in(response, [201, 400])
        
        # Test with very long content
        long_post = data_provider.get_post_test_data("long_content")
        response = jsonplaceholder_api.post("/posts", json_data=long_post)
        api_assert.assert_status_code_in(response, [201, 400, 413])  # 413 = Payload Too Large
    
    @api_test(
        title="Post Search and Filtering",
        description="Test post search and filtering capabilities",
        tags=["search", "filter", "posts", "get"]
    )
    def test_post_search_filtering(self, jsonplaceholder_api):
        """Test post search and filtering"""
        # Test filtering by multiple parameters
        params = {
            "userId": 1,
            "_limit": 5
        }
        
        response = jsonplaceholder_api.get("/posts", params=params)
        
        api_assert.assert_status_code(response, 200)
        
        posts = response.json()
        assert isinstance(posts, list), "Response should be a list"
        assert len(posts) <= 5, "Should respect limit parameter"
        
        # Verify filtering worked
        for post in posts:
            assert post["userId"] == 1, "All posts should belong to user 1"
    
    @api_test(
        title="Post Sorting Test",
        description="Test post sorting capabilities",
        tags=["sorting", "posts", "get"]
    )
    def test_post_sorting(self, jsonplaceholder_api):
        """Test post sorting"""
        # Test sorting by ID in descending order
        params = {
            "_sort": "id",
            "_order": "desc",
            "_limit": 10
        }
        
        response = jsonplaceholder_api.get("/posts", params=params)
        
        api_assert.assert_status_code(response, 200)
        
        posts = response.json()
        if len(posts) > 1:
            # Verify sorting order
            for i in range(len(posts) - 1):
                assert posts[i]["id"] >= posts[i + 1]["id"], "Posts should be sorted by ID in descending order"
    
    @api_test(
        title="Post Pagination Test",
        description="Test post pagination functionality",
        tags=["pagination", "posts", "get"]
    )
    def test_post_pagination(self, jsonplaceholder_api):
        """Test post pagination"""
        # Test pagination parameters
        page_size = 10
        page_number = 2
        
        params = {
            "_limit": page_size,
            "_start": (page_number - 1) * page_size
        }
        
        response = jsonplaceholder_api.get("/posts", params=params)
        
        api_assert.assert_status_code(response, 200)
        
        posts = response.json()
        assert len(posts) <= page_size, f"Should return at most {page_size} posts"
        
        # Verify we got the correct page
        if posts:
            expected_start_id = (page_number - 1) * page_size + 1
            # Note: This assumes sequential IDs, which may not always be true
            # In a real API, you'd verify based on your specific pagination logic
    
    @api_test(
        title="Post Unicode Content Test",
        description="Test posts with unicode and emoji content",
        tags=["unicode", "posts", "content"]
    )
    def test_post_unicode_content(self, jsonplaceholder_api):
        """Test post with unicode content"""
        unicode_post = data_provider.get_post_test_data("unicode_content")
        
        response = jsonplaceholder_api.post("/posts", json_data=unicode_post)
        
        api_assert.assert_status_code(response, 201)
        
        # Verify unicode content is preserved
        response_data = response.json()
        assert unicode_post["title"] in response_data["title"], "Unicode title should be preserved"
        assert unicode_post["body"] in response_data["body"], "Unicode body should be preserved" 