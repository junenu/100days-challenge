import { Marked } from 'marked';
import chalk from 'chalk';
import Table from 'cli-table3';
import stringWidth from 'string-width';

const INDENT = '  ';

function renderInline(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.+?)\*\*/g, (_, s) => chalk.bold(s))
    .replace(/__(.+?)__/g, (_, s) => chalk.bold(s))
    .replace(/\*(.+?)\*/g, (_, s) => chalk.italic(s))
    .replace(/_(.+?)_/g, (_, s) => chalk.italic(s))
    .replace(/`(.+?)`/g, (_, s) => chalk.bgGray.white(` ${s} `))
    .replace(/\[(.+?)\]\((.+?)\)/g, (_, label, url) =>
      `${chalk.cyan(label)} ${chalk.gray(`(${url})`)}`,
    );
}

function stripAnsi(str) {
  return str.replace(/\x1b\[[0-9;]*m/g, '');
}

function displayWidth(str) {
  return stringWidth(stripAnsi(str));
}

function renderTable(token) {
  const header = token.header.map((cell) => chalk.bold.yellow(renderInline(cell.text)));
  const colWidths = header.map((h) => Math.max(displayWidth(h) + 2, 6));

  token.rows.forEach((row) => {
    row.forEach((cell, i) => {
      const w = displayWidth(renderInline(cell.text)) + 2;
      if (w > colWidths[i]) colWidths[i] = w;
    });
  });

  const table = new Table({
    head: header,
    colWidths,
    style: { head: [], border: ['gray'] },
  });

  token.rows.forEach((row) => {
    table.push(row.map((cell) => renderInline(cell.text)));
  });

  return table.toString();
}

function renderInlineTokens(tokens) {
  if (!tokens || tokens.length === 0) return '';
  return tokens
    .map((t) => {
      switch (t.type) {
        case 'strong': return chalk.bold(renderInlineTokens(t.tokens));
        case 'em': return chalk.italic(renderInlineTokens(t.tokens));
        case 'codespan': return chalk.bgGray.white(` ${t.text} `);
        case 'link': return `${chalk.cyan(renderInlineTokens(t.tokens))} ${chalk.gray(`(${t.href})`)}`;
        case 'text': return t.tokens ? renderInlineTokens(t.tokens) : t.text;
        case 'escape': return t.text;
        default: return t.raw || t.text || '';
      }
    })
    .join('');
}

function renderToken(token, listDepth = 0) {
  switch (token.type) {
    case 'heading': {
      const level = token.depth;
      const text = token.tokens ? renderInlineTokens(token.tokens) : renderInline(token.text);
      if (level === 1) return '\n' + chalk.bold.magenta(`${'#'.repeat(level)} ${text}`) + '\n';
      if (level === 2) return '\n' + chalk.bold.cyan(`${'#'.repeat(level)} ${text}`) + '\n';
      if (level === 3) return '\n' + chalk.bold.blue(`${'#'.repeat(level)} ${text}`);
      return '\n' + chalk.bold(`${'#'.repeat(level)} ${text}`);
    }

    case 'paragraph':
      return '\n' + (token.tokens ? renderInlineTokens(token.tokens) : renderInline(token.text)) + '\n';

    case 'text':
      return token.tokens ? renderInlineTokens(token.tokens) : renderInline(token.text || token.raw || '');

    case 'code': {
      const lang = token.lang ? chalk.gray(` ${token.lang}`) : '';
      const border = chalk.gray('─'.repeat(60));
      const lines = token.text
        .split('\n')
        .map((l) => chalk.green(INDENT + l))
        .join('\n');
      return `\n${chalk.gray('┌')}${lang}${border}\n${lines}\n${chalk.gray('└' + '─'.repeat(60))}\n`;
    }

    case 'blockquote': {
      const inner = token.tokens
        ? token.tokens.map((t) => renderToken(t)).join('')
        : token.text;
      return inner
        .split('\n')
        .map((l) => chalk.gray('│ ') + chalk.italic(l))
        .join('\n') + '\n';
    }

    case 'list': {
      const start = token.start ?? 1;
      const lines = token.items.map((item, idx) => {
        const prefix = token.ordered
          ? chalk.yellow(`${start + idx}.`)
          : chalk.yellow('•');
        const indent = INDENT.repeat(listDepth + 1);
        const body = item.tokens
          ? item.tokens.map((t) => renderToken(t, listDepth + 1)).join('').trim()
          : renderInline(item.text);
        return `${indent}${prefix} ${body}`;
      });
      return '\n' + lines.join('\n') + '\n';
    }

    case 'table':
      return '\n' + renderTable(token) + '\n';

    case 'hr':
      return '\n' + chalk.gray('─'.repeat(60)) + '\n';

    case 'space':
      return '';

    case 'html':
      return chalk.gray(token.text);

    default:
      if (token.tokens) {
        return token.tokens.map((t) => renderToken(t, listDepth)).join('');
      }
      return token.raw || '';
  }
}

export function renderMarkdown(source) {
  const marked = new Marked();
  const tokens = marked.lexer(source);
  return tokens.map((t) => renderToken(t)).join('');
}
