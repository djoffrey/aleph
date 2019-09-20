import { combineReducers } from 'redux';

import metadata from './metadata';
import session from './session';
import config from './config';
import statistics from './statistics';
import entities from './entities';
import entityReferences from './entityReferences';
import entityTags from './entityTags';
import documentContent from './documentContent';
import collections from './collections';
import collectionStatus from './collectionStatus';
import collectionPermissions from './collectionPermissions';
import collectionXrefIndex from './collectionXrefIndex';
import collectionXrefMatches from './collectionXrefMatches';
import results from './results';
import alerts from './alerts';
import groups from './groups';
import notifications from './notifications';
import queryLogs from './queryLogs';
import dashboard from './dashboard';

const rootReducer = combineReducers({
  metadata,
  session,
  config,
  statistics,
  entities,
  entityReferences,
  documentContent,
  alerts,
  groups,
  notifications,
  entityTags,
  collections,
  collectionStatus,
  collectionPermissions,
  collectionXrefIndex,
  collectionXrefMatches,
  queryLogs,
  results,
  dashboard,
});

export default rootReducer;
