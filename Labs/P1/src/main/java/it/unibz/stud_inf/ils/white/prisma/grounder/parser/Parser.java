package it.unibz.stud_inf.ils.white.prisma.grounder.parser;

import it.unibz.stud_inf.ils.white.prisma.antlr.FormulaBaseVisitor;
import it.unibz.stud_inf.ils.white.prisma.antlr.FormulaLexer;
import it.unibz.stud_inf.ils.white.prisma.antlr.FormulaParser;
import it.unibz.stud_inf.ils.white.prisma.grounder.*;
import org.antlr.v4.runtime.*;

import java.util.stream.Collectors;

public class Parser {
	public static Formula parse(String formula) {
		CharStream charStream = CharStreams.fromString(formula);
		FormulaLexer lexer = new FormulaLexer(charStream);
		TokenStream tokens = new CommonTokenStream(lexer);
		FormulaParser parser = new FormulaParser(tokens);

		FormulaVisitor formulaVisitor = new FormulaVisitor();
		Formula traverseResult = formulaVisitor.visit(parser.formula());
		return traverseResult;
	}

	private static class FormulaVisitor extends FormulaBaseVisitor<Formula> {
		@Override
		public Formula visitFormula(FormulaParser.FormulaContext ctx) {
			final ExpressionVisitor visitor = new ExpressionVisitor();
			return new Formula(ctx.expression().stream().map(visitor::visit).collect(Collectors.toList()));
		}
	}

	private static class ExpressionVisitor extends FormulaBaseVisitor<Expression> {
		private BinaryConnectiveExpression wrap(BinaryConnectiveExpression.Connective connective, FormulaParser.ExpressionContext left, FormulaParser.ExpressionContext right) {
			return new BinaryConnectiveExpression(
				BinaryConnectiveExpression.Connective.OR,
				visit(left),
				visit(right)
			);
		}

		private QuantifiedExpression wrap(Quantifier quantifier, FormulaParser.ExpressionContext scope) {
			return new QuantifiedExpression(
				quantifier,
				new Variable(raw),
				visit(scope)
			);
		}

		@Override
		public Expression visitIdentifier(FormulaParser.IdentifierContext ctx) {
			return super.visitIdentifier(ctx);
		}

		@Override
		public Expression visitOr(FormulaParser.OrContext ctx) {
			return wrap(BinaryConnectiveExpression.Connective.OR, ctx.left, ctx.right);
		}

		@Override
		public Expression visitForall(FormulaParser.ForallContext ctx) {
			return wrap(Quantifier.FORALL, ctx.scope);
		}

		@Override
		public Expression visitFalse(FormulaParser.FalseContext ctx) {
			return super.visitFalse(ctx);
		}

		@Override
		public Expression visitIff(FormulaParser.IffContext ctx) {
			return wrap(BinaryConnectiveExpression.Connective.IFF, ctx.left, ctx.right);
		}

		@Override
		public Expression visitThen(FormulaParser.ThenContext ctx) {
			return wrap(BinaryConnectiveExpression.Connective.THEN, ctx.left, ctx.right);
		}

		@Override
		public Expression visitParenthesis(FormulaParser.ParenthesisContext ctx) {
			return visit(ctx.subexpression);
		}

		@Override
		public Expression visitNot(FormulaParser.NotContext ctx) {
			return new NegatedExpression(visit(ctx.subexpression));
		}

		@Override
		public Expression visitAnd(FormulaParser.AndContext ctx) {
			return wrap(BinaryConnectiveExpression.Connective.AND, ctx.left, ctx.right);
		}

		@Override
		public Expression visitTrue(FormulaParser.TrueContext ctx) {
			return super.visitTrue(ctx);
		}

		@Override
		public Expression visitVariable(FormulaParser.VariableContext ctx) {
			return super.visitVariable(ctx);
		}

		@Override
		public Expression visitExists(FormulaParser.ExistsContext ctx) {
			return wrap(Quantifier.EXISTS, ctx.scope);
		}

		@Override
		public Expression visitXor(FormulaParser.XorContext ctx) {
			return wrap(BinaryConnectiveExpression.Connective.XOR, ctx.left, ctx.right);
		}

		@Override
		public Expression visitAtom(FormulaParser.AtomContext ctx) {
			return new Atom(predicate, terms);
		}

		@Override
		public Expression visitIf(FormulaParser.IfContext ctx) {
			return wrap(BinaryConnectiveExpression.Connective.IF, ctx.left, ctx.right);
		}

		@Override
		public Expression visitTernary(FormulaParser.TernaryContext ctx) {
			return new TernaryExpression(
				visit(ctx.condition),
				visit(ctx.truthy),
				visit(ctx.falsy)
			);
		}
	}
}
