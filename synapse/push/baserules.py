# Copyright 2015, 2016 OpenMarket Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from synapse.push.rulekinds import PRIORITY_CLASS_MAP, PRIORITY_CLASS_INVERSE_MAP


def list_with_base_rules(rawrules):
    ruleslist = []

    # shove the server default rules for each kind onto the end of each
    current_prio_class = PRIORITY_CLASS_INVERSE_MAP.keys()[-1]

    ruleslist.extend(make_base_prepend_rules(
        PRIORITY_CLASS_INVERSE_MAP[current_prio_class]
    ))

    for r in rawrules:
        if r['priority_class'] < current_prio_class:
            while r['priority_class'] < current_prio_class:
                ruleslist.extend(make_base_append_rules(
                    PRIORITY_CLASS_INVERSE_MAP[current_prio_class]
                ))
                current_prio_class -= 1
                if current_prio_class > 0:
                    ruleslist.extend(make_base_prepend_rules(
                        PRIORITY_CLASS_INVERSE_MAP[current_prio_class]
                    ))

        ruleslist.append(r)

    while current_prio_class > 0:
        ruleslist.extend(make_base_append_rules(
            PRIORITY_CLASS_INVERSE_MAP[current_prio_class]
        ))
        current_prio_class -= 1
        if current_prio_class > 0:
            ruleslist.extend(make_base_prepend_rules(
                PRIORITY_CLASS_INVERSE_MAP[current_prio_class]
            ))

    return ruleslist


def make_base_append_rules(kind):
    rules = []

    if kind == 'override':
        rules = BASE_APPEND_OVRRIDE_RULES
    elif kind == 'underride':
        rules = BASE_APPEND_UNDERRIDE_RULES
    elif kind == 'content':
        rules = BASE_APPEND_CONTENT_RULES

    return rules


def make_base_prepend_rules(kind):
    rules = []

    if kind == 'override':
        rules = BASE_PREPEND_OVERRIDE_RULES

    return rules


BASE_APPEND_CONTENT_RULES = [
    {
        'rule_id': 'global/content/.m.rule.contains_user_name',
        'conditions': [
            {
                'kind': 'event_match',
                'key': 'content.body',
                'pattern_type': 'user_localpart'
            }
        ],
        'actions': [
            'notify',
            {
                'set_tweak': 'sound',
                'value': 'default',
            }, {
                'set_tweak': 'highlight'
            }
        ]
    },
]


BASE_PREPEND_OVERRIDE_RULES = [
    {
        'rule_id': 'global/override/.m.rule.master',
        'enabled': False,
        'conditions': [],
        'actions': [
            "dont_notify"
        ]
    }
]


BASE_APPEND_OVRRIDE_RULES = [
    {
        'rule_id': 'global/override/.m.rule.suppress_notices',
        'conditions': [
            {
                'kind': 'event_match',
                'key': 'content.msgtype',
                'pattern': 'm.notice',
                '_id': '_suppress_notices',
            }
        ],
        'actions': [
            'dont_notify',
        ]
    }
]


BASE_APPEND_UNDERRIDE_RULES = [
    {
        'rule_id': 'global/underride/.m.rule.call',
        'conditions': [
            {
                'kind': 'event_match',
                'key': 'type',
                'pattern': 'm.call.invite',
                '_id': '_call',
            }
        ],
        'actions': [
            'notify',
            {
                'set_tweak': 'sound',
                'value': 'ring'
            }, {
                'set_tweak': 'highlight',
                'value': False
            }
        ]
    },
    {
        'rule_id': 'global/underride/.m.rule.contains_display_name',
        'conditions': [
            {
                'kind': 'contains_display_name'
            }
        ],
        'actions': [
            'notify',
            {
                'set_tweak': 'sound',
                'value': 'default'
            }, {
                'set_tweak': 'highlight'
            }
        ]
    },
    {
        'rule_id': 'global/underride/.m.rule.room_one_to_one',
        'conditions': [
            {
                'kind': 'room_member_count',
                'is': '2',
                '_id': 'member_count',
            },
            {
                'kind': 'event_match',
                'key': 'type',
                'pattern': 'm.room.message',
                '_id': '_message',
            }
        ],
        'actions': [
            'notify',
            {
                'set_tweak': 'sound',
                'value': 'default'
            }, {
                'set_tweak': 'highlight',
                'value': False
            }
        ]
    },
    {
        'rule_id': 'global/underride/.m.rule.invite_for_me',
        'conditions': [
            {
                'kind': 'event_match',
                'key': 'type',
                'pattern': 'm.room.member',
                '_id': '_member',
            },
            {
                'kind': 'event_match',
                'key': 'content.membership',
                'pattern': 'invite',
                '_id': '_invite_member',
            },
            {
                'kind': 'event_match',
                'key': 'state_key',
                'pattern_type': 'user_id'
            },
        ],
        'actions': [
            'notify',
            {
                'set_tweak': 'sound',
                'value': 'default'
            }, {
                'set_tweak': 'highlight',
                'value': False
            }
        ]
    },
    # This is too simple: https://matrix.org/jira/browse/SYN-607
    # Removing for now
    # {
    #     'rule_id': 'global/underride/.m.rule.member_event',
    #     'conditions': [
    #         {
    #             'kind': 'event_match',
    #             'key': 'type',
    #             'pattern': 'm.room.member',
    #             '_id': '_member',
    #         }
    #     ],
    #     'actions': [
    #         'notify', {
    #             'set_tweak': 'highlight',
    #             'value': False
    #         }
    #     ]
    # },
    {
        'rule_id': 'global/underride/.m.rule.message',
        'conditions': [
            {
                'kind': 'event_match',
                'key': 'type',
                'pattern': 'm.room.message',
                '_id': '_message',
            }
        ],
        'actions': [
            'notify', {
                'set_tweak': 'highlight',
                'value': False
            }
        ]
    }
]


for r in BASE_APPEND_CONTENT_RULES:
    r['priority_class'] = PRIORITY_CLASS_MAP['content']
    r['default'] = True

for r in BASE_PREPEND_OVERRIDE_RULES:
    r['priority_class'] = PRIORITY_CLASS_MAP['override']
    r['default'] = True

for r in BASE_APPEND_OVRRIDE_RULES:
    r['priority_class'] = PRIORITY_CLASS_MAP['override']
    r['default'] = True

for r in BASE_APPEND_UNDERRIDE_RULES:
    r['priority_class'] = PRIORITY_CLASS_MAP['underride']
    r['default'] = True
