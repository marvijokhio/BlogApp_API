
## Feature Requirement: Adding the functionality of different roles of authors of a blog post.
<br><br>

 ### Changes in Database: 
 <br>
 <ol>
 <li>
    Add a new file named role.py in db/models directory for creating a model for a role. The model class should be named as "Role" with three basic attributes- 'id' as primary key with integer data type, 'name' with string data type and nullable=false, and'permissions' to add infromation about some privileges to be assigned for specific role. The permissions attribute has data type string, which is a comma-separated list of keywords representing a permission set. For example, if role is editor and he is only allowed to read and update the blog post, then the data value for permissions attribute would be "read, update". 
    <br><br>
    In order to create a custom role for a user, the owner of the post can select permissions (from a list of permissions) to set the previlages for that role. The permission list will contain all the permissions to be granted to a user, except the delete permission. For instance, the permissions list can contain permissions as follows but not limited to,
    <br><br>
    <ul>
    <li>Read</li>
    <li>Update</li>
    <li>Invite authors to the post</li>
    <li>Change roles of authors</li>
    <li>Remove any author(s)</li>
    <li>. . . . . </li>
    </ul>
    <br><br>
    When an owner invites a user as an author, the default permissions for that author can be 'read' and 'update'.
    </li>
    <li>
    Modify the UserPost table by adding the third column from Role table's primary key 'id' and name it as 'role_id'. The 'role_id' is forign key in UserPost table.
    </li>
    </ol>

### Changes in PATCH route:
<br>
<ol>
    <li>
    1. If the logged-in user is the author of the blog post then fetch the type of author's role from UserPost using it's 'role_id'. 
    </li>
    <li>
    2. Next, fetch the permission set of current author's role using permissions attibute. Now, allow the author to perform operations one by one depending on the particular previlages from permissions granted to the user. This can be achieved by writing independent blocks of codes for a particular previladge to verify the access grant first and then allow to perform that particular operation.
        <ul>
        <li>
        If the author is superuser then allow the user to update post, invite authors (readers only), approve comments etc. 
        </li>
        <li>
        If the author is editor then just allow updating the text and tags attributes.
        </li>
        <li>
        If the author is reader then only allow reading.
        </li>
        <li>
        If it's a custom role then we need to check individual permision and allow particular update operation.
        </li>
        </ul>
    </li>
    <li>
    3. We will need multi-threading/concurrent processing to perform operations on the particlar post becuase at a time more then one author may be working on same post and changing text or anything. It needs synchronization/await. 
    </li>
<ol>





