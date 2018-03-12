package it.unibz.stud_inf.ils.white.prisma.grounder.parser;

import it.unibz.stud_inf.ils.white.prisma.antlr.FormulaBaseVisitor;
import it.unibz.stud_inf.ils.white.prisma.antlr.FormulaLexer;
import it.unibz.stud_inf.ils.white.prisma.antlr.FormulaParser;
import it.unibz.stud_inf.ils.white.prisma.grounder.*;
import org.antlr.v4.runtime.*;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import static java.util.Collections.emptyList;

public class Parser {
	public static Formula parse(String formula) {
		CharStream charStream = CharStreams.fromString(formula);
		FormulaLexer lexer = new FormulaLexer(charStream);
		TokenStream tokens = new CommonTokenStream(lexer);
		FormulaParser parser = new FormulaParser(tokens);

		FormulaVisitor formulaVisitor = new FormulaVisitor();
		return formulaVisitor.visit(parser.formula());
	}

	private static class FormulaVisitor extends FormulaBaseVisitor<Formula> {
		@Override
		public Formula visitFormula(FormulaParser.FormulaContext ctx) {
			final ExpressionVisitor visitor = new ExpressionVisitor();
			return new Formula(ctx.expression().stream().map(visitor::visit).collect(Collectors.toList()));
		}
	}

	private static class ExpressionVisitor extends FormulaBaseVisitor<Expression> {
		@Override
		public Expression visitQuantification(FormulaParser.QuantificationContext ctx) {
			DomainVisitor visitor = new DomainVisitor();

			return new QuantifiedExpression(
				Quantifier.valueOf(ctx.quantifier.getText().toUpperCase()),
				new Variable(ctx.variable.getText().substring(1)),
				visitor.visit(ctx.range),
				visit(ctx.scope)
			);
		}

		@Override
		public Expression visitBinary(FormulaParser.BinaryContext ctx) {
			return new BinaryConnectiveExpression(
				BinaryConnectiveExpression.Connective.fromOperator(ctx.op.getText()),
				visit(ctx.left),
				visit(ctx.right)
			);
		}

		@Override
		public Expression visitFalse(FormulaParser.FalseContext ctx) {
			return super.visitFalse(ctx);
		}

		@Override
		public Expression visitParenthesizedExpression(FormulaParser.ParenthesizedExpressionContext ctx) {
			return visit(ctx.subexpression);
		}

		@Override
		public Expression visitUnary(FormulaParser.UnaryContext ctx) {
			return new NegatedExpression(visit(ctx.subexpression));
		}

		@Override
		public Expression visitTrue(FormulaParser.TrueContext ctx) {
			return super.visitTrue(ctx);
		}

		@Override
		public Expression visitVariableExpression(FormulaParser.VariableExpressionContext ctx) {
			return new Variable(ctx.variable.getText().substring(1));
		}

		public List<Term> wrap(FormulaParser.TermsContext ctx) {
			if (ctx == null) {
				return emptyList();
			}

			TermVisitor visitor = new TermVisitor();

			final List<Term> terms = new ArrayList<>();
			do  {
				FormulaParser.TermContext term = ctx.term();
				terms.add(visitor.visit(term));
			} while ((ctx = ctx.terms()) != null);

			return terms;
		}

		@Override
		public Expression visitAtom(FormulaParser.AtomContext ctx) {
			return new Atom(ctx.predicate.getText(), wrap(ctx.terms()));
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

	private static class DomainVisitor extends FormulaBaseVisitor<Domain> {
		public List<Term> wrap(FormulaParser.TermsContext ctx) {
			if (ctx == null) {
				return emptyList();
			}

			TermVisitor visitor = new TermVisitor();

			final List<Term> terms = new ArrayList<>();
			do  {
				FormulaParser.TermContext term = ctx.term();
				terms.add(visitor.visit(term));
			} while ((ctx = ctx.terms()) != null);

			return terms;
		}

		@Override
		public Domain visitRange(FormulaParser.RangeContext ctx) {
			IntExpressionVisitor visitor = new IntExpressionVisitor();

			// TODO: Do not collapse integer expressions at this point.
			return new IntegerDomain(
				visitor.visit(ctx.lower).toInteger(),
				visitor.visit(ctx.upper).toInteger()
			);
		}

		@Override
		public Domain visitSet(FormulaParser.SetContext ctx) {
			return new TermDomain(wrap(ctx.terms()));
		}
	}

	private static class TermVisitor extends FormulaBaseVisitor<Term> {
		@Override
		public Term visitConstant(FormulaParser.ConstantContext ctx) {
			return new ConstantTerm(ctx.getText());
		}

		@Override
		public Term visitVariableTerm(FormulaParser.VariableTermContext ctx) {
			return new VariableTerm(ctx.getText());
		}

		@Override
		public Term visitArithmetic(FormulaParser.ArithmeticContext ctx) {
			return super.visitArithmetic(ctx);
		}
	}

	private static class IntExpressionVisitor extends FormulaBaseVisitor<IntExpression> {
		@Override
		public IntExpression visitAbs(FormulaParser.AbsContext ctx) {
			return new IntUnaryConnectiveExpression(IntUnaryConnectiveExpression.Connective.ABS, visit(ctx.subexpression));
		}

		@Override
		public IntExpression visitMinus(FormulaParser.MinusContext ctx) {
			return new IntUnaryConnectiveExpression(IntUnaryConnectiveExpression.Connective.NEG, visit(ctx.subexpression));
		}

		@Override
		public IntExpression visitIntBinary(FormulaParser.IntBinaryContext ctx) {
			return new IntBinaryConnectiveExpression(
				visit(ctx.left),
				IntBinaryConnectiveExpression.Connective.fromOperator(ctx.op.getText()),
				visit(ctx.right)
			);
		}

		@Override
		public IntExpression visitNumber(FormulaParser.NumberContext ctx) {
			return new IntNumberExpression(Integer.parseInt(ctx.number.getText()));
		}

		@Override
		public IntExpression visitVariableIntExpression(FormulaParser.VariableIntExpressionContext ctx) {
			return new IntVariable(ctx.variable.getText().substring(1));
		}
	}
}
