============
SPADE PubSub
============

.. image:: https://img.shields.io/pypi/v/spade_pubsub.svg
    :target: https://pypi.python.org/pypi/spade_pubsub

.. image:: https://img.shields.io/pypi/pyversions/spade_pubsub.svg
    :target: https://pypi.python.org/pypi/spade_pubsub
    :alt: Python Versions

.. image:: https://img.shields.io/github/languages/count/javipalanca/spade_pubsub?label=languages
    :alt: Languages
    :target: https://pepy.tech/project/spade_pubsub

.. image:: https://img.shields.io/github/languages/code-size/javipalanca/spade_pubsub
    :alt: Code Size
    :target: https://pepy.tech/project/spade_pubsub

.. image:: https://img.shields.io/pypi/l/spade_pubsub
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

.. image:: https://pepy.tech/badge/spade_pubsub
    :target: https://pepy.tech/project/spade_pubsub
    :alt: Downloads

.. image:: https://github.com/javipalanca/spade/actions/workflows/python-package.yml/badge.svg
    :target: https://github.com/javipalanca/spade_pubsub/actions/workflows/python-package.yml
    :alt: Continuous Integration Status

.. image:: https://coveralls.io/repos/github/javipalanca/spade_pubsub/badge.svg?branch=master
    :target: https://coveralls.io/github/javipalanca/spade_pubsub?branch=master
    :alt: Code Coverage Status

.. image:: https://readthedocs.org/projects/spade_pubsub/badge/?version=latest
    :target: https://spade-pubsub.readthedocs.io?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/pypi/format/spade.svg
    :target: https://pypi.python.org/pypi/spade_pubsub


SPADE Plugin for PubSub support.
SPADE PubSub is a plugin that extends the SPADE (Smart Python Agent Development Environment) framework with publish-subscribe communication capabilities. It enables SPADE agents to leverage the XMPP PubSub extension for efficient, decoupled communication patterns in multi-agent systems.

Purpose and Scope
-----------------
This plugin provides a clean, agent-oriented interface to the XMPP Publish-Subscribe Extension (XEP-0060), allowing SPADE agents to:

* Create and manage PubSub nodes
* Subscribe to nodes of interest
* Publish content to nodes
* Receive notifications when content is published
* Manage subscriptions and published items

SPADE PubSub serves as a bridging layer between SPADE's agent-oriented architecture and the underlying XMPP Pu


* Free software: MIT license
* Documentation: https://spade-pubsub.readthedocs.io.


Features
--------

- **Node Creation and Management**: Agents can create, delete, and purge nodes on a PubSub server, allowing flexible management of communication channels.

- **Subscription to Nodes**: Agents have the capability to subscribe and unsubscribe from specific nodes, facilitating the reception of relevant updates.

- **Item Publication**: Agents can publish items to subscribed nodes, efficiently distributing information to all subscribers.

- **Item Management**: It's possible to retrieve all items published on a node and retract specific items when necessary.

- **Notifications Without Items**: Agents can send notifications to all subscribers of a node without the need to publish an item, useful for alerts or signals.

- **Custom Callbacks**: Functions can be registered to handle events such as item publication or retraction, allowing personalized responses to these events.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
