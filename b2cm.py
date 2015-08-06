#!/usr/bin/env python3

import sys
import xml.etree.ElementTree as etree
import collections
import os.path as path
import functools as ft
import glob
import argparse
import io

from mako.template import Template
from mako.runtime import Context
from mako.lookup import TemplateLookup

def usage(args=sys.argv[1:]):
	parser = argparse.ArgumentParser()
	parser.add_argument('--debug', action="store_true", default=False)
	parser.add_argument('block_path', help='path to block')

	return parser.parse_args(args)

metadata = {}
platforms = {'*': {} }
BASE_DIR = None
TEMPLATE_DIR = path.abspath(
	path.join(
		path.dirname(__file__),
		'templates'
	)
)

def resolve_relative_path(p):
	return path.join(
		BASE_DIR,
		p
	)

def register_platform_support(n):
	os = 'os' in n.attrib and n.attrib['os'] or None
	compiler = 'compiler' in n.attrib and n.attrib['compiler'] or None
	if os not in platforms:
		platforms[os] = {}
	if compiler:
		platforms[os][compiler] = {}

def add_to_config(section, config, directive, resolved_path=None):
	if section not in config:
		config[section] = []

	path_to_add = resolved_path
	if not path_to_add:
		path_to_add = resolve_relative_path(directive.text)

	entry = { 'path': path_to_add } 
	for attr in PATH_ATTRIBS:
		if attr in directive.attrib:
			entry[attr] = directive.attrib[attr]

	config[section].append(entry)

def add_framework_to_config(config, directive):
	if 'sdk' in directive.attrib and directive.attrib['sdk'] == 'true':
		add_to_config('framework', config, directive, directive.text)
	else:
		add_to_config('framework', config, directive)

def read_platform_specific_configuration(n):
	os = 'os' in n.attrib and n.attrib['os'] or None
	if not os:
		raise Exception("Unknown OS in {0}".format(n))

	for directive in n:
		if directive.tag in PLATFORM_TAGS:
			PLATFORM_TAGS[directive.tag](platforms[os], directive)
		else:
			print(directive)

def read_config_specific_configuration(platform, directive):
	config = directive.attrib.get('config', None)
	compiler = directive.attrib.get('compiler', None)

	if not config:
		raise Exception("Unknown config in {0}".format(directive))

	if config not in platform:
		platform[config] = {}

	if compiler:
		platform[config]['compiler'] = compiler

	for n in directive:
		if n.tag in PLATFORM_TAGS and n.tag != 'platform':
			PLATFORM_TAGS[n.tag](platform[config], n)
		else:
			print(etree.dump(n))

def add_glob_path(section, config, n):
	glob_pattern = resolve_relative_path(n.text)
	for x in glob.glob(glob_pattern):
		add_to_config(section, config, n, resolved_path=x)

PATH_ATTRIBS = [
    'absolute',
    'sdk',
    'cinder',
    'system',
    'replaceName',
]

IGNORE_TAGS = [
    'copyExclude'
]

PLATFORM_TAGS = {
	'platform': read_config_specific_configuration,
	'staticLibrary': ft.partial(add_to_config, 'static_libraries'),
	'framework': add_framework_to_config
}

SUPPORTED_TAGS = {
	'supports': register_platform_support,
	'includePath': ft.partial(add_to_config, 'include_paths', platforms['*']),
	'header': ft.partial(add_to_config, 'headers', platforms['*']),
	'source': ft.partial(add_to_config, 'source', platforms['*']),
	'headerPattern': ft.partial(add_glob_path, 'headers', platforms['*']),
	'sourcePattern': ft.partial(add_glob_path, 'source', platforms['*']),
	'asset': ft.partial(add_to_config, 'assets', platforms['*']),
	'platform': read_platform_specific_configuration
}

METADATA = [
  'name',
  'id',
  'git',
  'author',
  'version'
]

def main():
	args = usage()
	BASE_DIR = args.block_path

	tree = etree.parse(resolve_relative_path('cinderblock.xml'))
	root = tree.getroot()
	assert root.tag == 'cinder'
	block = None
	for child in root:
		if child.tag == 'block':
			block = child

	if not block:
		raise Exception('A valid cinder block was not found')

	for attr, value in block.attrib.items():
		if attr in METADATA:
			metadata[attr] = value

	for n in block:
		if n.tag in SUPPORTED_TAGS:
			SUPPORTED_TAGS[n.tag](n)
		elif n.tag not in IGNORE_TAGS:
			print('Unhandled tag: ', n)

	if (args.debug):
		import pprint ; pprint.pprint(platforms, indent=1)
	lookup = TemplateLookup(directories=[TEMPLATE_DIR])
	template = lookup.get_template('cmake.txt')
	buf = io.StringIO()
	context = Context(buf, platforms=platforms, metadata=metadata)
	template.render_context(context)
	print(buf.getvalue())

if __name__ == '__main__':
	main()
