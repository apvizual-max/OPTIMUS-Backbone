const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const {
  buildHeader,
  buildSummary,
  cleanTitle,
  detectStress,
  buildExpertise,
  buildAchievements,
  pickLinks,
  hasWord,
  FAMILY_TITLE,
  RULES,
  FACTS,
  LINKS
} = require('./cv-mutator.js');

describe('ALEX-KIT/cv-mutator unit tests', () => {

  test('hasWord detects exact word boundaries without matching substrings', () => {
    // 'ai' must not match inside 'said', 'train', 'chain', 'air'
    assert.equal(hasWord('I said hello', 'ai'), false);
    assert.equal(hasWord('riding the train', 'ai'), false);
    assert.equal(hasWord('fresh air', 'ai'), false);
    assert.equal(hasWord('working with AI models', 'ai'), true);
    assert.equal(hasWord('ai engineer needed', 'ai'), true);
    assert.equal(hasWord('build ai-augmented tools', 'ai'), true);

    // 'app' must not match inside 'apply' or 'apple'
    assert.equal(hasWord('Please apply here', 'app'), false);
    assert.equal(hasWord('Mobile app design', 'app'), true);

    // 'ui' must not match inside 'build' or 'gui'
    assert.equal(hasWord('build the product', 'ui'), false);
    assert.equal(hasWord('clean UI design', 'ui'), true);

    // 'ux' must not match inside 'flux' or 'luxury'
    assert.equal(hasWord('user flux', 'ux'), false);
    assert.equal(hasWord('great UX research', 'ux'), true);
  });

  test('FAMILY_TITLE mapping is deterministic in buildHeader', () => {
    const familyKeys = Object.keys(FAMILY_TITLE);
    assert.ok(familyKeys.length > 0, 'FAMILY_TITLE should have defined keys');

    for (const familyKey of familyKeys) {
      const expectedTitle = FAMILY_TITLE[familyKey];
      const header = buildHeader({
        family: familyKey,
        role: 'Any Role Name That Should Be Overridden By Family',
        jd: 'looking for senior designer'
      });
      assert.ok(
        header.headline.startsWith(expectedTitle),
        `Header title for family "${familyKey}" should start with "${expectedTitle}", got "${header.headline}"`
      );
    }
  });

  test('buildHeader handles placeholder [ROLE]', () => {
    const headerWithPlaceholder = buildHeader({
      role: '[ROLE]',
      family: 'art-director',
      jd: 'Senior Art Director needed for agency'
    });
    assert.ok(headerWithPlaceholder.headline.startsWith('Senior Art Director'));

    const headerWithBracketRole = buildHeader({
      role: 'Role [Placeholder]',
      jd: 'Looking for Graphic Design expert in print'
    });
    assert.ok(headerWithBracketRole.headline.startsWith('Senior Print & DTP Specialist') || headerWithBracketRole.headline.startsWith('Senior Graphic Designer'));
  });

  test('every specialization key from detectStress is present in all 4 tables', () => {
    // Collect all potential stress keys by probing keywords or checking internal structures
    const sampleJDs = [
      'social media content creator instagram',
      'artificial intelligence generative ai prompt engineering comfy',
      'brand system design ops governance template',
      'ui ux product dashboard interface figma',
      'advertising agency campaign creative',
      'video motion premiere runway capcut',
      'print dtp prepress packaging large-format',
      'presentation proposal data viz report',
      'generic role description without specific stress keywords'
    ];

    const detectedKeys = new Set();
    for (const jdText of sampleJDs) {
      const stress = detectStress(jdText);
      detectedKeys.add(stress.key);
    }

    assert.ok(detectedKeys.has('social'));
    assert.ok(detectedKeys.has('ai'));
    assert.ok(detectedKeys.has('brand'));
    assert.ok(detectedKeys.has('ux'));
    assert.ok(detectedKeys.has('creative'));
    assert.ok(detectedKeys.has('video'));
    assert.ok(detectedKeys.has('print'));
    assert.ok(detectedKeys.has('deck'));
    assert.ok(detectedKeys.has('core'));

    for (const key of detectedKeys) {
      const stressObj = { key };
      const summary = buildSummary(stressObj, '');
      assert.ok(summary && typeof summary === 'string' && summary.length > 0, `Missing summary for key: ${key}`);

      const expertise = buildExpertise(stressObj, '');
      assert.ok(Array.isArray(expertise), `Expertise for key ${key} is not an array`);
      assert.equal(expertise.length, 9, `Expertise for key ${key} should contain exactly 9 items`);

      const achievements = buildAchievements(stressObj);
      assert.ok(Array.isArray(achievements), `Achievements for key ${key} is not an array`);
      assert.equal(achievements.length, 3, `Achievements for key ${key} should contain exactly 3 items`);
    }
  });

  test('cleanTitle determines title correctly with AI priority', () => {
    // Text containing both AI and print keywords should prioritize AI
    assert.equal(cleanTitle('AI print designer'), 'AI-Augmented Design Lead');
    assert.equal(cleanTitle('Creative director and generative prompt engineering'), 'AI-Augmented Design Lead');
    assert.equal(cleanTitle('Art director'), 'Senior Art Director');
    assert.equal(cleanTitle('DTP prepress specialist'), 'Senior Print & DTP Specialist');
    assert.equal(cleanTitle('Video motion graphics'), 'Senior Video & Motion Designer');
    assert.equal(cleanTitle('Social media manager'), 'Senior Social Media Designer');
    assert.equal(cleanTitle('Presentation pitch designer'), 'Senior Presentation Designer');
    assert.equal(cleanTitle('Brand lead'), 'Senior Brand Designer');
    assert.equal(cleanTitle('Product UI UX designer'), 'Senior Product Designer');
    assert.equal(cleanTitle('Visual designer'), 'Senior Visual Designer');
    assert.equal(cleanTitle('Graphic designer'), 'Senior Graphic Designer');
    assert.equal(cleanTitle('Unknown position'), 'Senior Designer');
  });

  test('detectStress accurately selects stress profile', () => {
    assert.equal(detectStress('looking for social media content creator').key, 'social');
    assert.equal(detectStress('experienced in generative ai and comfy ui').key, 'ai');
    assert.equal(detectStress('building scalable brand system').key, 'brand');
    assert.equal(detectStress('ui ux product designer for web dashboard').key, 'ux');
    assert.equal(detectStress('advertising agency campaign creative').key, 'creative');
    assert.equal(detectStress('video motion graphics premiere').key, 'video');
    assert.equal(detectStress('print dtp prepress packaging').key, 'print');
    assert.equal(detectStress('presentation proposal pitch deck').key, 'deck');
    assert.equal(detectStress('general role').key, 'core');
  });

  test('buildExpertise produces 3x3 grid (9 items) and ranks matching JD keywords', () => {
    const stress = { key: 'ux' };
    const expertiseDefault = buildExpertise(stress, '');
    assert.equal(expertiseDefault.length, 9);

    // Test JD keyword boosting
    const expertiseBoosted = buildExpertise(stress, 'ag-Grid data accessibility');
    assert.equal(expertiseBoosted.length, 9);
    assert.ok(
      expertiseBoosted[0].includes('ag-Grid') || expertiseBoosted[0].includes('Accessibility'),
      'Keywords in JD should rank relevant expertise items higher'
    );
  });

  test('buildAchievements produces exactly 3 achievements', () => {
    const keys = ['brand', 'ux', 'ai', 'creative', 'video', 'print', 'deck', 'core', 'social'];
    for (const key of keys) {
      const achievements = buildAchievements({ key });
      assert.equal(achievements.length, 3, `Key ${key} should have exactly 3 achievements`);
      achievements.forEach(ach => {
        assert.ok(typeof ach === 'string' && ach.length > 10, 'Achievement should be a non-empty string');
      });
    }
  });

  test('pickLinks returns valid non-invented links and capped at 4', () => {
    const links = pickLinks('brand identity ui ux photography video motion ecommerce leadership');
    assert.ok(links.length <= 4, 'Should cap at maximum 4 links');
    assert.ok(links.length > 0, 'Should return at least 1 link');

    const knownUrls = new Set([...Object.values(LINKS), 'proof of work provided on request']);
    for (const link of links) {
      assert.ok(knownUrls.has(link.url), `Link URL ${link.url} is not in known LINKS database`);
      assert.ok(typeof link.label === 'string' && link.label.length > 0);
    }
  });

  test('buildHeader builds valid object matching RULES without network dependencies', () => {
    const jd = {
      role: 'Senior Product Designer',
      family: 'product-designer',
      jd: 'Figma design systems, UI/UX, WCAG compliance',
      notes: 'Remote position'
    };

    const header = buildHeader(jd);
    assert.ok(header.headline);
    assert.ok(header.summary);
    assert.ok(Array.isArray(header.expertise));
    assert.equal(header.expertise.length, RULES.expertise.exactCount);
    assert.ok(Array.isArray(header.achievements));
    assert.equal(header.achievements.length, RULES.achievements.exactCount);
    assert.ok(Array.isArray(header.links));
    assert.ok(header.links.length <= 4);
    assert.deepEqual(header.rules, RULES);

    // Verify word count limits from rules
    const summaryWordCount = header.summary.trim().split(/\s+/).length;
    assert.ok(summaryWordCount <= RULES.summary.maxWords, `Summary word count (${summaryWordCount}) exceeded maxWords (${RULES.summary.maxWords})`);
  });

});
