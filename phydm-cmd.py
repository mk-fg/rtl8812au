#!/usr/bin/env python3

import itertools as it, operator as op, functools as ft
import os, sys, pathlib, logging, contextlib, readline, re


proc_base = '/proc/net/rtl8812au/'
proc_odm_cmd = 'odm/cmd'


class LogMessage:
	def __init__(self, fmt, a, k): self.fmt, self.a, self.k = fmt, a, k
	def __str__(self): return self.fmt.format(*self.a, **self.k) if self.a or self.k else self.fmt

class LogStyleAdapter(logging.LoggerAdapter):
	def __init__(self, logger, extra=None):
		super().__init__(logger, extra or {})
	def log(self, level, msg, *args, **kws):
		if not self.isEnabledFor(level): return
		log_kws = {} if 'exc_info' not in kws else dict(exc_info=kws.pop('exc_info'))
		msg, kws = self.process(msg, kws)
		self.logger.log(level, LogMessage(msg, args, kws), **log_kws)

get_logger = lambda name: LogStyleAdapter(logging.getLogger(name))


def dump_constants(p):
	drv_rates = [
		'1M', '2M', '5_5M', '11M', '6M', '9M', '12M', '18M', '24M', '36M', '48M', '54M',
		'MCS0', 'MCS1', 'MCS2', 'MCS3', 'MCS4', 'MCS5', 'MCS6', 'MCS7', 'MCS8', 'MCS9',
		'MCS10', 'MCS11', 'MCS12', 'MCS13', 'MCS14', 'MCS15', 'MCS16', 'MCS17', 'MCS18', 'MCS19',
		'MCS20','MCS21', 'MCS22', 'MCS23', 'MCS24', 'MCS25', 'MCS26', 'MCS27', 'MCS28', 'MCS29',
		'MCS30', 'MCS31',
		'VHTSS1MCS0', 'VHTSS1MCS1', 'VHTSS1MCS2', 'VHTSS1MCS3', 'VHTSS1MCS4',
		'VHTSS1MCS5', 'VHTSS1MCS6', 'VHTSS1MCS7', 'VHTSS1MCS8', 'VHTSS1MCS9',
		'VHTSS2MCS0', 'VHTSS2MCS1', 'VHTSS2MCS2', 'VHTSS2MCS3', 'VHTSS2MCS4',
		'VHTSS2MCS5', 'VHTSS2MCS6', 'VHTSS2MCS7', 'VHTSS2MCS8', 'VHTSS2MCS9',
		'VHTSS3MCS0', 'VHTSS3MCS1', 'VHTSS3MCS2', 'VHTSS3MCS3', 'VHTSS3MCS4',
		'VHTSS3MCS5', 'VHTSS3MCS6', 'VHTSS3MCS7', 'VHTSS3MCS8', 'VHTSS3MCS9',
		'VHTSS4MCS0', 'VHTSS4MCS1', 'VHTSS4MCS2', 'VHTSS4MCS3', 'VHTSS4MCS4',
		'VHTSS4MCS5', 'VHTSS4MCS6', 'VHTSS4MCS7', 'VHTSS4MCS8', 'VHTSS4MCS9' ]

	if p:
		p = pathlib.Path(p)
		if p.name == 'hal_com.h':
			def parse_hal_com_data_rates(p):
				rates = dict()
				for line in p.read_text().splitlines():
					m = re.search(r'^#define\s+DESC_RATE(\S+)\s+0x(\S+)\s*$', line)
					if not m: continue
					rates[int(m.group(2), 16)] = m.group(1)
				return list(rates.get(n) for n in range(max(rates.keys())+1))
			drv_rates = parse_hal_com_data_rates(p)
		else: raise ValueError(f'Dont know how/what to parse (from) file: {p}')

	print('List of TX rates (as "decimal_id rate"):')
	for n, rate in enumerate(drv_rates): print(f'  {n:02d} {rate}')


class ReadlineQuery:

	prompt = '> '

	def log_debug_errors(func):
		@ft.wraps(func)
		def _wrapper(self, *args, **kws):
			try: return func(self, *args, **kws)
			except Exception as err:
				if not self.log.isEnabledFor(logging.DEBUG): raise
				self.log.exception('readline callback error: {}', err)
		return _wrapper

	def __init__(self, opts_base=None):
		self.log = get_logger('readline')
		self.opts, self.opts_cmd = opts_base or list(), list()

	def __enter__(self):
		self.init()
		return self
	def __exit__(self, *err): pass

	def init(self):
		readline.set_completer_delims('')
		readline.set_completer(self.rl_complete)
		readline.parse_and_bind('tab: complete')

	@log_debug_errors
	def rl_complete(self, text, state):
		if state == 0:
			opts = self.opts_cmd or self.opts
			self.matches = ( opts[:] if not text else
				list(s for s in opts if s and s.startswith(text)) )
		# self.log.debug('{} from {}', [text, state], self.matches)
		try: return self.matches[state]
		except IndexError: return None

	def input(self, query=None, options=None):
		if options: self.opts_cmd = list(options)
		if query: print(query)
		return input(self.prompt)


def get_command_list(node):
	cmd_list = list()
	node.write_text('-h\n')
	cmd_help = iter(node.read_text(errors='replace').splitlines())
	cmd_help = it.dropwhile(lambda s: s != 'BB cmd ==>', cmd_help)
	for line in cmd_help:
		if not line: break
		m = re.search(r'^\s*(\d+)\s*:\s*(\S+)', line)
		if not m: continue
		code, cmd = m.groups()
		cmd_list.append(cmd)
	return cmd_list

def console_read_loop(node, dst=None):
	if not dst: dst = sys.stdout
	while True:
		info = node.read_text(errors='replace')
		if info.strip() == 'GET, nothing to print': break
		dst.write(info)

def console_loop(node):
	log = get_logger('console')

	log.debug('Building command-completion list...')
	cmd_list = get_command_list(node)
	log.debug('Command completions: {}', cmd_list)

	log.debug('Initializing readline console...')
	print(
		'Input uses libreadline (history, inputrc, etc),'
		' double-tab for command completion. "-h" to list commands.' )
	with ReadlineQuery(cmd_list) as rlq,\
			contextlib.suppress(EOFError, KeyboardInterrupt):
		while True:
			log.debug('Checking output...')
			console_read_loop(node)
			log.debug('Querying new input...')
			cmd = rlq.input()
			log.debug('cmd: {!r}', cmd)
			if cmd: node.write_text(cmd)
	print()


def main(args=None):
	node = pathlib.Path(proc_base)

	import argparse
	parser = argparse.ArgumentParser(
		description='Interactive console for rtl8812au driver phydm_cmd debug interface.')
	parser.add_argument('-i', '--iface', metavar='iface',
		help=f'Network interface name to access under {node}/.'
			' Default - pick first one that is there.')
	parser.add_argument('-p', '--odm-cmd-path', metavar='path',
		help=f'Full path to specific {node}/.../{proc_odm_cmd} node to use.'
			' Overrides -i/--iface option. Default is to pick one for any iface that is there.')
	parser.add_argument('-c', '--cmd', action='append', metavar='command',
		help='Command(s) to send non-interactively and exit.'
			' Same as doing echo to {proc_odm_cmd} node, disables interactive console.'
			' Can be specified multiple times, commands will be sent in the same order.')
	parser.add_argument('-x', '--const',
		nargs='?', const=True, metavar='path',
		help='Parse/print various constants from driver code and exit.'
			' Run without arg to dump hard-coded'
				' list of constants, without re-parsing them from headers.'
			' Things to parse: .../include/hal_com.h')
	parser.add_argument('-d', '--debug', action='store_true', help='Verbose operation mode.')
	opts = parser.parse_args(sys.argv[1:] if args is None else args)

	logging.basicConfig(level=logging.DEBUG if opts.debug else logging.WARNING)
	log = get_logger('main')

	if opts.const:
		p = opts.const if opts.const is not True else None
		return dump_constants(p)

	if opts.odm_cmd_path: node = pathlib.Path(opts.odm_cmd_path)
	elif opts.iface: node = node / opts.iface / proc_odm_cmd
	else:
		glob_mask = f'*/{proc_odm_cmd}'
		node_list = sorted(node.glob(glob_mask))
		log.debug( 'Matching phydm_cmd interface'
			' via glob: {} (matches: {})', node / glob_mask, len(node_list) )
		if not node_list:
			parser.error(f'Failed to match any phydm_cmd nodes via: {node / glob_mask}')
		node = node_list[0]
	log.debug('Using phydm_cmd node path: {}', node)

	if opts.cmd:
		for cmd in opts.cmd:
			log.debug('cmd: {!r}', cmd)
			node.write_text(cmd + '\n')
			console_read_loop(node)
		return

	console_loop(node)

if __name__ == '__main__': sys.exit(main())
