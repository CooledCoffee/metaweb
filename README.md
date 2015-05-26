Introduction
============

MetaWeb is a web framework built on other web frameworks.
Currently it supports web.py and webapp2 (thus also Google App Engine).

Installation
============

pip install metaweb

Hello World
===========

A website consist of views. A view is simply a python function denoted by a decorator.

	from metaweb.views import View
	
	@View
	def hello():
	    return 'hello'

The @View decorator is written with the <a href="https://github.com/CooledCoffee/decorated" target="_blank">decorated</a> framework.
The result of the decorator is not a traditional python function.
But the decorated framework makes sure it acts, in many ways, very similar to a python function.
This means you can call it like a function.
More important, you can test it like a function.
For the reason we will go through later, you need to put this code in a "views" module.

The next step is to start a web server and start making http requests.
We create a server module like this:

	from metaweb.impls import webpy
	
	webpy.run()

Start the server by running

	python server.py
	
Now you can access the view by opening http://localhost:8080/hello in your browser.

Arguments
=========

MetaWeb parses query strings from GET requests and form values from POST requests.
The results are mapped to arguments of the view functions.
Update your views module like this:

	from metaweb.views import View
	
	@View
	def hello(name):
	    return 'hello ' + name

Restart your server. Open http://localhost:8080/hello?name=world in your browser.
The view will return "hello world" as response.
You can do the same thing with a POST request and the response will be the same.

Pages & APIs
============

Normally you don't use the @View decorator directly.
Instead, you use its subordinates. There are two of them namely @page & @api.
@page is similar to @View except that it automatically sets the Content-Type header to "text/html; charset=utf-8".
@api, however, is a little trickier.

First, @api assumes the arguments are json encoded and automatically decode them.
Update your views module like this

	from metaweb import api
	
	@api
	def hello(name, with_dot=False):
	    result = 'hello ' + name
	    if with_dot:
	        result += '.'
	    return result

Test it with http://localhost:8080/hello?name="world"&with\_dot=true.
The name field with are decoded to a python string "world" while the with\_dot decoded to a python boolean true.
Also note that the with_dot has a default value.
When the field is omitted in the request, it gets a default value False.

Second, the response is also json encoded.
You may notice that the response is now quoted.
The @api also sets the Content-Type header to "application/json".

URL Mapping
===========

Most python web frameworks maintain mapping between urls and views.
You can use regular expressions in the mapping.
This is very flexible but not convenient.
It gets difficult to maintain when you are building large sites with tons of url mappings.

In contrast, metaweb takes the old php/.net approach.
It automatically infers the corresponding url of a view based on its position.
For example, all of these functions map to the /math/add url:

* An add function in the views.math module

* An add function in the views.math.root module

* A root function in the views.math.add module

All views must sit within the views package/module, otherwise they are simply ignored.
You cannot use regular expressions here. Flexibility is sacrificed in exchange of convenience here.

If you are building a small website with only top-level urls,
you can squeeze all your views in a views module.
This is what we do in our previous examples.

Sometimes, you may want to have urls like /users/ which automatically redirects to /users/home.
This can be achieved by

	from metaweb import page
	
	@page(default=True)
	def home():
	    return 'home'

In this case, the @page decorator actually creates two views:

* The first one mapped to /users/ and redirects to /users/home.

* The seconds one mapped to /users/home and returns the actual page.

In fact, according to the http standard, you can also use /users instead of /users/.
This, IMHO, is misleading because it gives the illusion that /users is a top-level view.
I don't recommend such uses. But it is supported by metaweb simply for compatibility.

Note that this redirect mechanism is only supported by @page.
There is no point for @api to support such behavior.

Author
======

Mengchen LEE: <a href="https://plus.google.com/117704742936410336204" target="_blank">Google Plus</a>, <a href="https://cn.linkedin.com/pub/mengchen-lee/30/8/23a" target="_blank">LinkedIn</a>
