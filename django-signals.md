Topic: [Django Signals](https://docs.djangoproject.com/en/3.2/topics/signals/#receiver-functions)
=================================================================================================

**1. By default are django signals executed synchronously or asynchronously? Please support your answer with a code snippet that conclusively proves your stance. The code does not need to be elegant and production ready, we just need to understand your logic.**

**Ans.** In Django 3.2 as well as other versions before 5.0, Signals are executed synchronously by default.
Though from version 5.0, It is possible to use Signal.asend() method for sending signals asynchronously and use async in the receiver function.

For synchronous:
```python
# intialize data in models.py
from django.db import models
from django.dispatch import receiver, Signal

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    content = models.TextField()

# rest of data handling
# manually define a signal
post_created = Signal()

# signal receiver function
@receiver(post_created)
def notify_user(sender, author, **kwargs):
    time.sleep(5)
    print(f"New post by {author}!")

def create_blog_post(title, author, content):
    post = BlogPost(title=title, author=author, content=content)
    post.save()
    post_created.send(sender=BlogPost, author=author)   # send a custom signal
    print("Post created and notified the users.")
```

The above code will wait 5 seconds before printing "Post created and notified the users" because the sending signals isnt asynchronous. The porgram will first execute the receiver function and then execute the print statement in the create_blog_post() function. This proves that by default, signals are asynchronous.

---

**2. Do django signals run in the same thread as the caller? Please support your answer with a code snippet that conclusively proves your stance. The code does not need to be elegant and production ready, we just need to understand your logic.**

**Ans.** Yes, django signals and the caller of the signal run in the same thread.

```python
from django.db import models
from django.dispatch import receiver, Signal
from django.utils.autoreload import threading

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    content = models.TextField()

# rest of data handling
# manually define a signal
post_created = Signal()

# signal receiver function
@receiver(post_created)
def notify_user(sender, author, **kwargs):
    print(f"New post by {author}!")
    print(f'Running in thread: {threading.currentThread().name}')

def create_blog_post(title, author, content):
    post = BlogPost(title=title, author=author, content=content)
    post.save()
    post_created.send(sender=BlogPost, author=author)   # send a custom signal
    print(f'Running in thread: {threading.currentThread().name}')
    """
    output:
    Running in thread: Thread-1 (process_request_thread) <- this for caller
    Running in thread: Thread-1 (process_request_thread) <- this for signal
    """
```
Name of thread in both caller and receiver function is same. Hence, django signals run in the same thread as the caller.

---

**3. By default do django signals run in the same database transaction as the caller? Please support your answer with a code snippet that conclusively proves your stance. The code does not need to be elegant and production ready, we just need to understand your logic.**

**Ans.** By default, django signals do not run in the same database transaction as the caller. Each SQL query runs in its own transaction.
But it is possible to run both in same transaction using either `transaction.atomic` decorator or `transaction.atomic` context manager.

```python
from django.db import models
from django.dispatch import receiver, Signal

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    content = models.TextField()

class Notification(models.Model):
    author = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    message = models.CharField(max_length=100)

post_created = Signal()

@receiver(post_created)
def notify_user(sender, author, **kwargs):
    message = f"New post by {author}!"
    notification = Notification(author=author, message=message * 100)   # 2. this query will fail as message column is exceeding its max_length (100)
    notification.save()
    print(message)

def create_blog_post(title, author, content):
    post = BlogPost(title=title, author=author, content=content)    # 1. db operation in the caller codeblock
    post.save()
    post_created.send(sender=BlogPost, author=author)
```

In the above code, the 1st query will execute successfully and commit the changes as well but, the 2nd query will fail as the message's column max_length is exceeding. Since the 2nd query failed, the program will roll back the database to the changes made by the 1st query.

Now, If both caller and signals were in the same transaction, the program would have reverted back the database to its original state (including changes made by the 1st query). This proves that django signals do not run in the same database transaction as the caller.
