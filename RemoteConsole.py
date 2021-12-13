from __future__ import absolute_import, print_function, unicode_literals
import time, sys, socket, code, re, traceback
if sys.version.startswith('2'): from StringIO import StringIO
else: from io import StringIO

u"""
todo: could use some clean up, plus doesn't work with multiple connects, IO / stdout redirection needs improving
"""

class RemoteConsole:
    u""" Allow non-blocking Python REPL """
    def __init__(self, ctx=None, port=10141, welcome="Remote Python REPL connected"):
        self.log('Initializing RemoteConsole on port', port)
        self.welcome = welcome
        self.context = dict(globals())
        self.context['remote_console'] = self
        if ctx:
            self.context.update(ctx)
        if 'self' not in self.context:
            self.context['self'] = self
        self.server_socket = None
        self.running = False
        self.port = port
        self.start_server()
        self.last_connect_check = 0.0
        self.interpreters = []
        self.clients = []

    def try_connect(self):
        try:
            conn, addr = self.server_socket.accept()
        except socket.error as socket_error:
            if socket_error.errno != 35:
                raise e
        else:
            self.send(conn, self.welcome + "\n>>> ")
            self.clients.append(conn)
            self.interpreters.append(code.InteractiveConsole(locals=self.context))
            self.interpreters[-1].push("\nimport types as rc_types\n\n")

    def start_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(('', self.port))
            self.server_socket.setblocking(False)
            self.server_socket.listen(1)
            self.running = True
        except BaseException as e:
            self.log("\n\n\n*** Server start failed:", e, "***\n\n\n")
            self.server_socket = None

    def tick(self):
        if not self.running:
            return
        if not self.server_socket:
            self.start_server()
        if time.time() - self.last_connect_check > 3.0:
            self.try_connect()
            self.last_connect_check = time.time()
        self.try_read_commands()

    def try_read_commands(self):
        for index, client in enumerate(self.clients):
            cmds = ""
            while True:
                try:
                    cmds += client.recv(4096).decode("ascii")
                except socket.error as socket_error:
                    if socket_error.errno != 35:
                        raise socket_error
                    break
            if cmds:
                self.execute_commands(index, client, cmds)

    def execute_commands(self, index, client, cmds):
        pattern = re.compile("^\\s*def\\s+([^(]+)\\(\\s*self\\s*[),]")
        self.log('Read command:\n', cmds)
        if pattern.search(cmds):
            cmds = cmds.lstrip()
        if cmds in ["quit\n", "exit\n"]:
            self.try_socket_close("client" + str(index), client)
            self.clients.remove(client)
        elif cmds == "shutdown\n":
            self.shutdown()
        else:
            incomplete, output, buffer = self.run_and_prompt(index, cmds)
            if not incomplete and len([line for line in buffer if pattern.search(line)]):
                method = pattern.search("\n".join(buffer)).group(1)
                cmd = "\n\nself.{} = rc_types.MethodType({}, self)\n\n".format(method, method)
                self.run_cmd(index, self.interpreters[index], cmd)

    def run_and_prompt(self, index, source):
        incomplete, output, buffer = self.run_cmd(index, self.interpreters[index], source)
        if incomplete:
            self.send(self.clients[index], "... ")
        else:
            self.send(self.clients[index], output)
            self.send(self.clients[index], ">>> ")
        return incomplete, output, buffer
    
    def send(self, conn, msg):
        conn.sendall(msg.encode("ascii"))

    """Temporarily hack replace std(out|err), since exec() is used by interp"""
    def run_cmd(self, index, interpreter, cmd):
        self.log("Executing:\n", cmd)
        stdout = sys.stdout
        stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        buffer = list(interpreter.buffer) + [cmd]
        incomplete = interpreter.push(cmd)
        output = sys.stdout.getvalue()
        output += sys.stderr.getvalue()
        sys.stdout = stdout
        sys.stderr = stderr
        self.log("Result:", incomplete, "\n", output)
        return incomplete, output, buffer

    def log(self, *args):
        print(*args)

    def shutdown(self):
        self.running = False
        self.log('Shutting down')
        for index, client in enumerate(self.clients):
            self.try_socket_close("client " + str(index), client)
        self.try_socket_close("server", self.server_socket)

    def try_socket_close(self, name, socket_instance):
        def sclose(action, callback):
            try:
                self.log("Executing", action)
                callback()
            except BaseException as e:
                self.log("Error during", action, e)
        sclose(name + " socket shutdown", lambda: socket_instance.shutdown(socket.SHUT_RDWR))
        sclose(name + " socket close", lambda: socket_instance.close())


if __name__ == "__main__":
    import signal, traceback, os
    ri = RemoteConsole(port=int(os.environ.get('RC_PORT') or '10141'))

    def signal_handler(sig, frame):
        ri.log("Shutdown hook")
        ri.shutdown()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    while ri.running:
        try:
            ri.tick()
        except BaseException as e:
            ri.log("Error ticking:", e)
            traceback.print_exc()
        time.sleep(0.100)


