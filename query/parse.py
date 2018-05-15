from typing import List

from antlr4 import *

from query.QueryLexer import QueryLexer
from query.QueryParser import QueryParser
from query.QueryVisitor import QueryVisitor


def make_function(outer_scope, argument_names: List[str], parser: QueryParser, prog: QueryParser.ProgContext):
    def function(*args):
        visitor = MyQueryVisitor(parser)
        visitor.memory = outer_scope.copy()
        for i in range(len(args)):
            visitor.memory[argument_names[i]] = args[i]
        return visitor.for_result(prog)

    return function


class Return(Exception):
    def __init__(self, thing):
        self.ret = thing


class MyQueryVisitor(QueryVisitor):
    def __init__(self, parser: QueryParser):
        self.memory = {
        }
        self.parser: QueryParser = parser
        self.last_expr = None

    def for_result(self, ctx):
        try:
            self.visit(ctx)
        except Return as ret:
            return ret.ret
        return self.last_expr

    def visitProg(self, ctx: QueryParser.ProgContext):
        for stat in ctx.getChildren(lambda child: isinstance(child, QueryParser.StatContext)):
            self.visit(stat)

    def visitFunc(self, ctx: QueryParser.FuncContext):
        args = ctx.arguments().getText()[:-2].split(',')
        return make_function(self.memory, args, self.parser, ctx.prog())

    def visitAssign(self, ctx):
        name = ctx.ID().getText()
        value = self.visit(ctx.expr())
        self.memory[name] = value
        return value

    def visitRawExpr(self, ctx: QueryParser.RawExprContext):
        value = self.visit(ctx.expr())
        self.last_expr = value
        return value

    def visitInt(self, ctx):
        return int(ctx.INT().getText())

    def visitId(self, ctx):
        name = ctx.ID().getText()
        if name in self.memory:
            return self.memory[name]
        return 0

    def visitAccess(self, ctx: QueryParser.AccessContext):
        thing = self.visit(ctx.expr())
        return getattr(thing, ctx.ID(), 0)

    def visitMulDiv(self, ctx):
        left = (self.visit(ctx.expr(0)))
        right = (self.visit(ctx.expr(1)))
        if ctx.op.type == QueryParser.MUL:
            return left * right
        return left / right

    def visitString(self, ctx: QueryParser.StringContext):
        return eval(ctx.getText())

    def visitAddSub(self, ctx):
        left = int(self.visit(ctx.expr(0)))
        right = int(self.visit(ctx.expr(1)))
        if ctx.op.type == QueryParser.ADD:
            return left + right
        return left - right

    def visitParens(self, ctx):
        return self.visit(ctx.expr())

    def visitCall(self, ctx: QueryParser.CallContext):
        to_call = self.visit(ctx.expr(0))
        args = [self.visit(arg) for arg in ctx.getChildren(lambda x: isinstance(x, QueryParser.ExprContext))][1:]
        return to_call(*args)

    def visit(self, tree):
        return super(MyQueryVisitor, self).visit(tree)


def parse(text, **kwargs):
    parser = QueryParser(CommonTokenStream(QueryLexer(InputStream(text))))
    tree = parser.prog()
    visitor = MyQueryVisitor(parser)
    for key, value in kwargs.items():
        visitor.memory[key] = value
    return visitor.for_result(tree)


if __name__ == '__main__':
    with open('debug.txt') as handle:
        content = handle.read()
    print(parse(content))
