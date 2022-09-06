from flask import jsonify, request, g, abort
from sqlalchemy import delete

from api import api
from db.shared import db
from db.models.user_post import UserPost
from db.models.post import Post

from db.utils import row_to_dict
from middlewares import auth_required
import nums_from_string

@api.post("/posts")
@auth_required
def posts():
    # validation
    user = g.get("user")
    if user is None:
        return abort(401)

    data = request.get_json(force=True)
    text = data.get("text", None)
    tags = data.get("tags", None)
    if text is None:
        return jsonify({"error": "Must provide text for the new post"}), 400

    # Create new post
    post_values = {"text": text}
    if tags:
        post_values["tags"] = tags

    post = Post(**post_values)
    db.session.add(post)
    db.session.commit()

    user_post = UserPost(user_id=user.id, post_id=post.id)
    db.session.add(user_post)
    db.session.commit()

    return row_to_dict(post), 200


"""
Route for fetching blog posts by authors: 

    Fetch blog posts that have at least one of the authors specified in the authorIds parameter in the request
        Note: a helper function named Post.getPostsByUserId (Javascript) and Post.get_posts_by_user_id for fetching blog posts by a single author have been provided for you to use.
    Sort the blog posts based on the provided query parameters (outlined below) and remove any duplicate blog posts (try to be efficient when doing this)
    Return the blog posts in the response

"""

@api.get("/posts/<authorIds>/", defaults = {"sortBy": "id", "direction": "asc"})
@api.get("/posts/<authorIds>/<sortBy>/", defaults = {"direction": "asc"})
@api.get("/posts/<authorIds>/<sortBy>/<direction>/")
@auth_required
def get_posts_by_author_ids(authorIds, sortBy, direction):
    # validation
    user = g.get("user")
    if user is None:
        return jsonify({"error": "User login required!"}), 401

    idList = [] # list to save authorIds

    # split authorIds input string to elements in list and convert to integer
    for id in authorIds.split(","):
        if id.isdigit():
            idList.append(int(id))
        else: 
            return jsonify({"error":"Ensure that the authorIds only contain digits"}), 400
    
    # Validation check for sortBy url parameter values
    if sortBy.lower() in ["id", "reads", "likes", "popularity"]:
        posts_found = []
        notusers = []
        for id in idList:
            try:
                user_posts = Post.get_posts_by_user_id(id)
            except:
                notusers.append(id)
                continue
        
            if user_posts:
                try:
                    for up in user_posts:
                        d = next(filter(lambda d: d.get("id") == up.id, posts_found), None) # skip duplicates: check if the current post already exits in list
                        if d is None:
                            post_data = {}
                            post_data['id'] = up.id
                            post_data['likes'] = up.likes
                            post_data['popularity'] = up.popularity
                            post_data['reads'] = up.reads 
                            post_data['authorIds'] = nums_from_string.get_nums("".join(map(str,up.users)))
                            post_data['tags'] = up.tags
                            post_data['text'] = up.text
                            posts_found.append(post_data)
                except:
                    return jsonify({"error":"The was something wrong on server side.. "}), 500
            else:
                continue

            if posts_found:
                #Validation for direction input parameter
                drc = False
                if direction.lower() == "desc":
                    drc = True
                elif direction.lower() == "asc":
                    drc = False
                else:
                    return jsonify({"error":"The value for direction can't be other then 'asc', 'desc' "}), 400
                
                posts_found.sort(key=lambda x: x[sortBy.lower()],reverse=drc)
            else:
                return jsonify({"error": "No post found!"}), 404
        
        if not posts_found:
            return jsonify({"error":"No posts found by this author(s)"}) ,404

        if len(notusers) == len(idList):
            return jsonify({"error":"No such author(s) exists!"}), 404
        else:
            return jsonify({"posts": posts_found})
    else:
        return jsonify({"error":"The value for sortBy can't be other then 'id', 'reads', 'likes', 'polularity' "}), 400


"""
The route for updating the blog post on following conditions: 
    Ensure only an author of a post can update the post
    Update the blog post, if it exists, in the database
    Return the updated blog post in the response

"""
@api.route('/posts/<postId>', methods=['PATCH'])
@auth_required
def change_user_post(postId):
    # argument validation
    if not postId.isdigit():
        return jsonify({"error": "The input id must be a digit."}), 400

    data = request.get_json(force=True)

    user = g.get("user")
    if user is None:
        return abort(401)
    
# json input data validation
    if request.data and data:
        text = data.get("text", None)
        tags = data.get("tags", None)
        authrs = data.get("authorIds", None)  # fetch authors from the input from user
        TextOk = 0
        TagsOk = 0
        authorIdsOk = 0

        if text is not None and len(text) > 5 and len(text) < 5000:
            TextOk = 1
        else:
            return jsonify({"error": "Invalid text input."}) , 400
        
        
        if tags in ("", [], [""], None, 0, False):
            return jsonify({"error":"Invalid input for tags!"}) , 400
        else:
            for tag in tags:
                tag = tag.strip()
                if tag.isalpha() and len(tag) > 1:
                    TagsOk = 1
                else:
                    return jsonify({"error":"The tags can only contain alphabets"}), 400


        if authrs in ("", [], [""], None, 0, False):
            return jsonify({"error":"Invalid input for authors!"}) , 400
        else:
            for authr in authrs:
                if isinstance(authr, int):
                    authorIdsOk = 1
                else:
                    return jsonify({"error":"The authorIds can not contain string input but only integers"}), 400

# json input data validation ends

# Updating the post if user is the author of post 
        post = Post.get_posts_by_post_id(postId)
        if post is None:
            return jsonify({"error":"No post found for this post id.."}) , 404  
        
        try:
                authors = nums_from_string.get_nums("".join(map(str,post.users)))  # fetching authors from the database
                
                if user.id in authors:    # Check if the user is the author of the post                    
                    # To change the taxt
                    if TextOk:
                        post.text = text
                    
                    # To change the tags
                    if TagsOk:
                        tags = [tag.strip() for tag in tags]
                        post.tags = tags

                    # To change the authors
                    if authorIdsOk:
                        if authrs:
                            toDel = list(set(authors) - set(authrs)) # gives the authors which need to be deleted from userpost with postId
                            toAdd = list(set(authrs) - set(authors)) # gives the authors which need to be added to userpost with postId

                            if toAdd:
                                for usr in toAdd:
                                    try:
                                        up = UserPost(user_id=usr, post_id=int(postId))
                                        db.session.add(up)
                                    except:
                                        return jsonify({"error":"Unable to change authors"}), 500

                                db.session.flush()                    
                                db.session.commit()
                                
                            if toDel:
                                for usr in toDel:
                                    try:
                                        stmt = delete(UserPost).where(UserPost.user_id == usr and UserPost.post_id == postId).execution_options(synchronize_session="fetch")
                                        db.session.execute(stmt)
                                    except:
                                        return jsonify({"error":"Unable to change authors"}), 500
                                    
                                    db.session.flush()
                                    db.session.commit()
                        
                    db.session.flush()
                    db.session.commit()
                else: 
                    return jsonify({"error": "The user is not the author of this post!"}), 400

                # creating json of the post to return in end.
                post_data = {}
                post_data['id'] = post.id
                post_data['likes'] = post.likes
                post_data['popularity'] = post.popularity
                post_data['reads'] = post.reads 
                post_data['authorIds'] = nums_from_string.get_nums("".join(map(str,post.users)))
                post_data['tags'] = post.tags
                post_data['text'] = post.text
                return jsonify({"Post Updated": post_data})

        except:
            return abort(500)
    return jsonify({"error": "No data is provided so nothing can be updated."}), 400
