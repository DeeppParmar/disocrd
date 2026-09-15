import { pgTable, bigint, boolean, varchar, text, jsonb, timestamp, integer, serial } from 'drizzle-orm/pg-core';

export const guilds = pgTable('guilds', {
  id: bigint('id', { mode: 'number' }).primaryKey(),
  name: varchar('name', { length: 255 }).notNull(),
  ownerId: bigint('owner_id', { mode: 'number' }).notNull(),
  joinedAt: timestamp('joined_at').defaultNow().notNull()
});

export const guildConfigs = pgTable('guild_configs', {
  guildId: bigint('guild_id', { mode: 'number' }).primaryKey().references(() => guilds.id),
  prefix: varchar('prefix', { length: 10 }).default('!').notNull(),
  language: varchar('language', { length: 10 }).default('en').notNull(),
  logChannelId: bigint('log_channel_id', { mode: 'number' }),
  modRoleIds: jsonb('mod_role_ids').default([]).notNull(),
  adminRoleIds: jsonb('admin_role_ids').default([]).notNull()
});

export const roleMappings = pgTable('role_mappings', {
  id: serial('id').primaryKey(),
  guildId: bigint('guild_id', { mode: 'number' }).notNull(),
  roleId: bigint('role_id', { mode: 'number' }).notNull(),
  type: varchar('type', { length: 50 }).notNull()
});

export const channelMappings = pgTable('channel_mappings', {
  id: serial('id').primaryKey(),
  guildId: bigint('guild_id', { mode: 'number' }).notNull(),
  channelId: bigint('channel_id', { mode: 'number' }).notNull(),
  type: varchar('type', { length: 50 }).notNull()
});

export const moderationCases = pgTable('moderation_cases', {
  id: serial('id').primaryKey(),
  guildId: bigint('guild_id', { mode: 'number' }).notNull(),
  userId: bigint('user_id', { mode: 'number' }).notNull(),
  modId: bigint('mod_id', { mode: 'number' }).notNull(),
  action: varchar('action', { length: 50 }).notNull(),
  reason: text('reason'),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

export const warnings = pgTable('warnings', {
  id: serial('id').primaryKey(),
  guildId: bigint('guild_id', { mode: 'number' }).notNull(),
  userId: bigint('user_id', { mode: 'number' }).notNull(),
  modId: bigint('mod_id', { mode: 'number' }).notNull(),
  reason: text('reason'),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

export const tickets = pgTable('tickets', {
  id: serial('id').primaryKey(),
  guildId: bigint('guild_id', { mode: 'number' }).notNull(),
  userId: bigint('user_id', { mode: 'number' }).notNull(),
  channelId: bigint('channel_id', { mode: 'number' }),
  status: varchar('status', { length: 50 }).notNull().default('open'),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

export const ticketConfigs = pgTable('ticket_configs', {
  guildId: bigint('guild_id', { mode: 'number' }).primaryKey(),
  categoryId: bigint('category_id', { mode: 'number' }),
  logChannelId: bigint('log_channel_id', { mode: 'number' }),
  supportRoleIds: jsonb('support_role_ids').default([]).notNull()
});

export const logEvents = pgTable('log_events', {
  id: serial('id').primaryKey(),
  guildId: bigint('guild_id', { mode: 'number' }).notNull(),
  category: varchar('category', { length: 50 }).notNull(),
  action: varchar('action', { length: 50 }).notNull(),
  details: jsonb('details').default({}).notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

export const securityEvents = pgTable('security_events', {
  id: serial('id').primaryKey(),
  guildId: bigint('guild_id', { mode: 'number' }).notNull(),
  eventType: varchar('event_type', { length: 50 }).notNull(),
  userId: bigint('user_id', { mode: 'number' }),
  details: jsonb('details').default({}).notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

export const backups = pgTable('backups', {
  id: serial('id').primaryKey(),
  guildId: bigint('guild_id', { mode: 'number' }).notNull(),
  data: jsonb('data').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

export const analyticsSnapshots = pgTable('analytics_snapshots', {
  id: serial('id').primaryKey(),
  guildId: bigint('guild_id', { mode: 'number' }).notNull(),
  date: timestamp('date').notNull(),
  memberCount: integer('member_count').notNull(),
  messagesSent: integer('messages_sent').notNull(),
  modActions: integer('mod_actions').notNull()
});

export const suggestions = pgTable('suggestions', {
  id: serial('id').primaryKey(),
  guildId: bigint('guild_id', { mode: 'number' }).notNull(),
  userId: bigint('user_id', { mode: 'number' }).notNull(),
  content: text('content').notNull(),
  status: varchar('status', { length: 50 }).notNull().default('pending'),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

export const scheduledTasks = pgTable('scheduled_tasks', {
  id: serial('id').primaryKey(),
  taskType: varchar('task_type', { length: 50 }).notNull(),
  guildId: bigint('guild_id', { mode: 'number' }),
  payload: jsonb('payload').default({}).notNull(),
  executeAt: timestamp('execute_at').notNull()
});

export const verificationConfigs = pgTable('verification_configs', {
  guildId: bigint('guild_id', { mode: 'number' }).primaryKey(),
  enabled: boolean('enabled').default(false).notNull(),
  roleId: bigint('role_id', { mode: 'number' }),
  channelId: bigint('channel_id', { mode: 'number' })
});
