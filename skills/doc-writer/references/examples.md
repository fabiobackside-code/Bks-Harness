# Doc Writer Examples

Use these examples to keep docs focused on contracts and maintainability.

## Example 1: Contract-Focused Docstring

### Input

A TypeScript function finalizes a cart. It writes totals, applies tax, and marks the cart as settled.

### Weak Output

```ts
/**
 * Takes the cartId string, loads the cart from the database, loops items,
 * adds tax, then saves and returns the cart object.
 * @param cartId - The cart id.
 * @returns The cart.
 */
export async function settleCart(cartId: string): Promise<Cart> {
  // ...
}
```

### Why This Is Weak

- Narrates implementation steps that can change.
- Repeats type information.
- Spends five lines where one would state the contract.

### Strong Output

```ts
/** Settles the cart for checkout: line totals with tax, cart marked as settled. */
export async function settleCart(cartId: string): Promise<Cart> {
  // ...
}
```

The errors (`CartNotFoundError`, `EmptyCartError`), the tables written and the fact that it does
not charge payment go in the module README or `ARCHITECTURE.md`.

### Why This Is Strong

- Describes the contract, not the algorithm, in one line.
- Leaves errors, side effects and preconditions to the document that already holds them.

## Example 2: Useful Inline Comment

### Input

Tax must run before loyalty discounts because finance rules depend on pre-discount taxable amounts.

### Weak Output

```ts
// Apply tax.
applyTax(lines);
// Apply loyalty.
applyLoyaltyDiscount(lines);
```

### Strong Output

```ts
// Tax must run before loyalty discounts; reversing the order double-counts
// exemptions on discounted lines.
applyTax(lines);
applyLoyaltyDiscount(lines);
```

### Why This Is Strong

- Explains why order matters.
- Prevents a future "cleanup" from changing behavior.
- Does not restate the function names.

## Example 3: README Setup Section

### Input

A project README starts with a long architecture essay and hides run commands near the bottom.

### Strong Output Shape

```md
# Project Name

One short paragraph explaining what this service/app does.

## Prerequisites

- Node.js version from `.nvmrc`
- Package manager used by the lockfile

## Install

`npm install`

## Configure

Copy `.env.example` to `.env` and fill required values.

## Run

`npm run dev`

## Test

`npm test`

## More Docs

- Architecture: `docs/architecture.md`
- API: `docs/api.md`
```

### Why This Is Strong

- New maintainers can get running quickly.
- Secrets are not embedded.
- Deeper material is linked, not duplicated.
