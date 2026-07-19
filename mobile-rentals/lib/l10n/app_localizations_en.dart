// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get navListings => 'Listings';

  @override
  String get navContracts => 'Contracts';

  @override
  String get navIndex => 'Index';

  @override
  String get navProfile => 'Profile';

  @override
  String get navBrowse => 'Browse';

  @override
  String get navApplications => 'Applications';

  @override
  String get fieldEmail => 'Email';

  @override
  String get fieldPassword => 'Password';

  @override
  String get fieldFullName => 'Full name';

  @override
  String get fieldPhone => 'Phone (Ethiopian)';

  @override
  String get hintPhoneFormat => '09xxxxxxxx or +2519xxxxxxxx';

  @override
  String get fieldSubCity => 'Sub-city';

  @override
  String get hintAnySubCity => 'Any sub-city';

  @override
  String get fieldFaydaId => 'Fayda ID number';

  @override
  String get hintFaydaId => 'Your national digital ID';

  @override
  String get hintPasswordRules => '8+ chars, an uppercase letter and a number';

  @override
  String get fieldAddress => 'Address';

  @override
  String get hintAddress => 'Building, street, area';

  @override
  String get fieldType => 'Type';

  @override
  String get fieldSubtype => 'Subtype';

  @override
  String get fieldArea => 'Area (m2)';

  @override
  String get fieldYearBuilt => 'Year built';

  @override
  String get hintOptional => 'Optional';

  @override
  String get fieldBedrooms => 'Bedrooms';

  @override
  String get fieldBathrooms => 'Bathrooms';

  @override
  String get fieldCondition => 'Condition';

  @override
  String get hintSelectCondition => 'Select condition';

  @override
  String get fieldOptionalMessage => 'Optional message';

  @override
  String get hintReviewerMessage => 'Anything the reviewer should know';

  @override
  String get fieldMapPin => 'Map pin (tap to place)';

  @override
  String get fieldMessageToOwner => 'Message to the owner (optional)';

  @override
  String get hintMessageToOwner => 'Introduce yourself, move-in date, etc.';

  @override
  String get fieldMaxRent => 'Max rent (ETB/month)';

  @override
  String get hintNoLimit => 'No limit';

  @override
  String get labelPhone => 'Phone';

  @override
  String get labelFaydaId => 'Fayda ID';

  @override
  String get labelPropertyType => 'Property type';

  @override
  String get labelFloors => 'Floors';

  @override
  String get labelPublished => 'Published';

  @override
  String get labelAreaM2 => 'm2 area';

  @override
  String get labelContract => 'Contract';

  @override
  String get labelMonthlyRent => 'Monthly rent';

  @override
  String get labelTerm => 'Term';

  @override
  String get labelDeposit => 'Deposit';

  @override
  String get labelDepositReceipt => 'Deposit receipt';

  @override
  String get labelYourOffer => 'Your offer';

  @override
  String get labelOffer => 'Offer';

  @override
  String get labelLimitReached => 'Limit reached';

  @override
  String get labelAny => 'Any';

  @override
  String get actionSignIn => 'Sign in';

  @override
  String get actionCancel => 'Cancel';

  @override
  String get actionAccept => 'Accept';

  @override
  String get actionDecline => 'Decline';

  @override
  String get actionDone => 'Done';

  @override
  String get actionRemove => 'Remove';

  @override
  String get actionAddPhoto => 'Add photo';

  @override
  String get actionAddShort => 'Add';

  @override
  String get actionChooseFromGallery => 'Choose from gallery';

  @override
  String get actionTakePhoto => 'Take a photo';

  @override
  String get actionManagePhotos => 'Manage photos';

  @override
  String get actionAgreement => 'Agreement';

  @override
  String get preparingEllipsis => 'Preparing...';

  @override
  String get actionViewApplications => 'View applications';

  @override
  String get actionRegisterProperty => 'Register a property';

  @override
  String get actionSubmitForReview => 'Submit for review';

  @override
  String get actionSubmitApplication => 'Submit application';

  @override
  String get actionApply => 'Apply';

  @override
  String get actionClearFilters => 'Clear filters';

  @override
  String get actionResetFilters => 'Reset filters';

  @override
  String get actionShowResults => 'Show results';

  @override
  String get actionDownloadContractPdf => 'Download contract PDF';

  @override
  String get preparingPdfEllipsis => 'Preparing PDF...';

  @override
  String get actionSignOut => 'Sign out';

  @override
  String get actionTryAgain => 'Try again';

  @override
  String get actionCreateAccountShort => 'Create account';

  @override
  String get welcomeCreateAccountCta => 'Create an account';

  @override
  String get authAlreadyHaveAccount => 'I already have an account';

  @override
  String get loginNewHerePrefix => 'New here?';

  @override
  String get validationFullName => 'Enter your full name.';

  @override
  String get validationEmail => 'Enter a valid email address.';

  @override
  String get validationPhone => 'Enter your phone number.';

  @override
  String get validationFaydaId => 'Enter your Fayda ID number.';

  @override
  String get validationPasswordLength =>
      'Password must be at least 8 characters.';

  @override
  String get validationPasswordUppercase =>
      'Password needs an uppercase letter.';

  @override
  String get validationPasswordNumber => 'Password needs a number.';

  @override
  String get validationAddress =>
      'Enter the full property address (at least 5 characters).';

  @override
  String get validationArea => 'Enter the area in square metres.';

  @override
  String validationPhotoLimit(int max) {
    return 'A property may have at most $max photos.';
  }

  @override
  String onePhotoOversized(int mb) {
    return 'One photo was over ${mb}MB and was not added.';
  }

  @override
  String multiplePhotosOversized(int count, int mb) {
    return '$count photos were over ${mb}MB and were not added.';
  }

  @override
  String photosPartiallyAdded(int remaining, int max) {
    return 'Only the first $remaining photos were added ($max max).';
  }

  @override
  String get screenTitleApplications => 'Applications';

  @override
  String get screenTitleMyListings => 'My listings';

  @override
  String get screenSubtitleMyListings => 'Properties you have put up for rent';

  @override
  String get screenTitlePhotos => 'Photos';

  @override
  String get screenTitleRegisterProperty => 'Register a property';

  @override
  String get screenTitleFindHome => 'Find a home';

  @override
  String get screenSubtitleFindHome => 'Verified listings across Addis Ababa';

  @override
  String get screenTitleAbout => 'About & the law';

  @override
  String get screenTitleActivity => 'Activity';

  @override
  String get screenTitleMyContracts => 'My contracts';

  @override
  String get screenSubtitleMyContracts => 'Registered tenancy agreements';

  @override
  String get screenTitleMyApplications => 'My applications';

  @override
  String get screenSubtitleMyApplications => 'Every offer you have made';

  @override
  String get screenTitleRentIndex => 'Rent index';

  @override
  String get screenSubtitleRentIndex => 'Median registered rents by sub-city';

  @override
  String get loginSubtitle => 'Sign in to your registry account';

  @override
  String get signupSubtitle => 'Create your registry account';

  @override
  String get signupTypeRenterTitle => 'Rent a home';

  @override
  String get signupTypeOwnerTitle => 'List a property';

  @override
  String get signupOwnerNote =>
      'Owner accounts are verified by a rental officer before a listing can be published. You can prepare listings right away.';

  @override
  String get welcomeAgency => 'Addis Ababa Housing Administration';

  @override
  String get welcomeHero =>
      'Rent a home at an honest, valuation-certified price. Every listing and contract is registered with the government.';

  @override
  String get welcomePoint1Title => 'Certified prices';

  @override
  String get welcomePoint1Body =>
      'A published band from an official valuation, not a broker guess.';

  @override
  String get welcomePoint2Title => 'Registered contracts';

  @override
  String get welcomePoint2Body =>
      'Written and registered under Proclamation 1320/2024.';

  @override
  String get welcomePoint3Title => 'A public rent index';

  @override
  String get welcomePoint3Body =>
      'See the median rent per sub-city before you decide.';

  @override
  String get welcomeHeroCaption => '28,000 ETB/mo · Bole';

  @override
  String get splashTagline => 'Government-mediated rental registry';

  @override
  String get emptyNoApplicationsTitle => 'No applications yet';

  @override
  String get ownerEmptyApplicationsMessage =>
      'When renters apply within your band, their offers appear here for you to accept or decline.';

  @override
  String get renterEmptyApplicationsMessage =>
      'When you apply to a listing, it will appear here so you can track the owner\'s decision.';

  @override
  String get emptyNoListingsTitle => 'List your first property';

  @override
  String get emptyNoListingsMessage =>
      'Register a property and we will suggest an honest rent band from an official valuation. An officer reviews it before it goes public.';

  @override
  String get emptyNoPhotosTitle => 'No photos yet';

  @override
  String emptyNoPhotosMessage(int max) {
    return 'Add up to $max real photos so renters see the actual unit, not a placeholder.';
  }

  @override
  String get emptyNoMatchesTitle => 'No matches yet';

  @override
  String get emptyNoMatchesFilteredMessage =>
      'No published listings fit these filters. Try widening your search.';

  @override
  String get emptyNoMatchesMessage =>
      'There are no published listings right now. Check back soon.';

  @override
  String get emptyActivityTitle => 'Nothing new';

  @override
  String get emptyActivityMessage =>
      'Status changes on your applications and contracts show up here. This updates automatically while the app is open.';

  @override
  String get emptyNoContractsTitle => 'No contracts yet';

  @override
  String get emptyNoContractsMessage =>
      'Once an application is accepted and an officer registers the tenancy, your contract will appear here with its PDF.';

  @override
  String get emptyIndexTitle => 'Index still building';

  @override
  String get emptyIndexMessage =>
      'The index publishes a median only where enough contracts have been registered. As the registry grows, medians per sub-city appear here.';

  @override
  String get errorLoadApplications => 'Could not load applications.';

  @override
  String get errorLoadListings => 'Could not load listings.';

  @override
  String get errorLoadPhotos => 'Could not load photos.';

  @override
  String get errorLoadListing => 'Could not load this listing.';

  @override
  String get errorLoadContracts => 'Could not load contracts.';

  @override
  String get errorLoadIndex => 'Could not load the index.';

  @override
  String get dialogAcceptTitle => 'Accept this applicant?';

  @override
  String dialogAcceptContent(String name, String rent) {
    return 'Accepting $name at $rent marks the listing as rented and declines the others. A rental officer then registers the contract.';
  }

  @override
  String get defaultRenterName => 'this renter';

  @override
  String get defaultApplicantLabel => 'Applicant';

  @override
  String get dialogRemovePhotoTitle => 'Remove this photo?';

  @override
  String get dialogCannotUndo => 'This cannot be undone.';

  @override
  String get snackApplicationAccepted =>
      'Accepted. An officer will register the contract.';

  @override
  String get snackApplicationDeclined => 'Application declined.';

  @override
  String snackApplicationSent(String price) {
    return 'Application sent at $price. Track it under Applications.';
  }

  @override
  String get verificationPendingTitle => 'Verification pending';

  @override
  String get verificationPendingMessage =>
      'A rental officer is reviewing your Fayda ID. You can prepare listings now, but they publish only after you are verified.';

  @override
  String officerNoteLabel(String reason) {
    return 'Officer note: $reason';
  }

  @override
  String publishedOnLabel(String date) {
    return 'Published $date';
  }

  @override
  String createdOnLabel(String date) {
    return 'Created $date';
  }

  @override
  String bandRangeLabel(String min, String max) {
    return 'Band $min - $max';
  }

  @override
  String get resultSubmittedTitle => 'Submitted for review';

  @override
  String get resultSubmittedMessage =>
      'A rental officer will verify the details and publish your listing at the band below.';

  @override
  String get onePhotoUploadFailed =>
      'One photo could not be uploaded. Add it from Manage photos on this listing.';

  @override
  String multiplePhotosUploadFailed(int count) {
    return '$count photos could not be uploaded. Add them from Manage photos on this listing.';
  }

  @override
  String get sectionLocation => 'Location';

  @override
  String get sectionProperty => 'Property';

  @override
  String get sectionPhotos => 'Photos';

  @override
  String get sectionNoteToOfficer => 'Note to the officer';

  @override
  String photoUploadHint(int mb, int max) {
    return 'Photos upload to the registry when you submit. JPG, PNG or WEBP, up to ${mb}MB each, $max max.';
  }

  @override
  String get applySheetTitle => 'Apply to rent';

  @override
  String get applyWithinBand => 'Within the allowed band';

  @override
  String get filterListingsLabel => 'Filter listings';

  @override
  String bedCount(int n) {
    return '$n bed';
  }

  @override
  String bathCount(int n) {
    return '$n bath';
  }

  @override
  String bedCountPlus(int n) {
    return '$n+';
  }

  @override
  String maxRentSummary(String price) {
    return '<= $price';
  }

  @override
  String get filterSheetTitle => 'Filter';

  @override
  String mapPinMissingInfo(int count, int total) {
    return '$count of $total listings have no map pin yet and are shown only in the list.';
  }

  @override
  String get perMonthSuffix => '/month';

  @override
  String get perMonthSuffixShort => '/mo';

  @override
  String get bandPanelTitle => 'Allowed rent band';

  @override
  String get bandPanelBody =>
      'You can apply at any amount inside this band. Offers outside it are not accepted. The band is set from an official valuation, not a broker.';

  @override
  String get propertyDetailsTitle => 'Property details';

  @override
  String get chooseYourOfferLabel => 'Choose your offer';

  @override
  String get aboutIntro =>
      'A government-mediated rental registry for Addis Ababa.';

  @override
  String get aboutLawTitle => 'The law: Proclamation 1320/2024';

  @override
  String get aboutLawBody =>
      'Ethiopia\'s Rent Control and Administration Proclamation requires residential rental contracts to be written and registered with the district housing administration. Rent increases are capped, and Addis Ababa set the ceiling at 11.5% for 2026/27. This app is the digital way to meet that mandate.';

  @override
  String get aboutCertifiedTitle => 'Certified prices, not broker guesses';

  @override
  String get aboutCertifiedBody =>
      'Every listing carries a rent band from an official valuation. You apply at any amount inside the band; owners choose a tenant, not a price war. There is no bidding.';

  @override
  String get aboutContractsBody =>
      'When an owner accepts you, a rental officer registers the tenancy and issues a contract with a public contract number. The contract becomes active once your deposit receipt is recorded at the administration.';

  @override
  String get aboutDataTitle => 'Your data';

  @override
  String get aboutDataBody =>
      'Your Fayda ID and phone are used to verify you and appear only on your own contracts, never on public listings. Officers verify owner accounts before a listing can be published.';

  @override
  String get aboutMissingTitle => 'What is not here yet';

  @override
  String get aboutMissingBody =>
      'Deposits are recorded, not held in custody, in this version. There is no in-app chat; contact details are on the registered contract. Photo upload and Amharic are on the way.';

  @override
  String get aboutFooter =>
      'Operated with the Addis Ababa Housing Administration';

  @override
  String get aboutSublabel => 'Proclamation 1320/2024 explained';

  @override
  String activityApplicationLabel(String address) {
    return 'Application · $address';
  }

  @override
  String activityContractLabel(String contractNo) {
    return 'Contract · $contractNo';
  }

  @override
  String termRangeLabel(String start, String end) {
    return '$start  ->  $end';
  }

  @override
  String get depositRecorded => 'Recorded';

  @override
  String get depositAwaiting => 'Awaiting record';

  @override
  String get contractActivatesNote =>
      'This contract activates once the officer records your deposit receipt at the housing administration.';

  @override
  String defaultListingLabel(String id) {
    return 'Listing $id';
  }

  @override
  String appliedOnLabel(String date) {
    return 'Applied $date';
  }

  @override
  String get roleOwner => 'Property owner';

  @override
  String get roleRenter => 'Renter';

  @override
  String get roleOfficer => 'Rental officer';

  @override
  String get roleCitizen => 'Citizen';

  @override
  String get defaultAccountName => 'Your account';

  @override
  String get statusVerified => 'Verified';

  @override
  String get statusVerificationPending => 'Pending';

  @override
  String get settingsLanguageLabel => 'Language';

  @override
  String get settingsLanguageSublabel => 'Choose the app language';

  @override
  String get languageEnglish => 'English';

  @override
  String get languageAmharic => 'አማርኛ';

  @override
  String indexIntroText(String period) {
    return 'Medians from registered tenancy contracts for $period. Low-sample cells are hidden, so what you see is real.';
  }

  @override
  String sampleSizeLabel(int n) {
    return 'n=$n';
  }

  @override
  String bandSpreadLabel(int percent) {
    return '$percent% band';
  }

  @override
  String suggestedPriceLabel(String price) {
    return 'Suggested $price';
  }

  @override
  String get photoPendingLabel => 'Photo pending';

  @override
  String get locationNotPinnedLabel => 'Location not pinned';

  @override
  String get certifiedBadgeLabel => 'Certified';

  @override
  String get statusPending => 'Pending';

  @override
  String get statusAccepted => 'Accepted';

  @override
  String get statusRejected => 'Not selected';

  @override
  String get statusWithdrawn => 'Withdrawn';

  @override
  String get statusDraft => 'Draft';

  @override
  String get statusPendingReview => 'Under review';

  @override
  String get statusPublished => 'Published';

  @override
  String get statusRented => 'Rented';

  @override
  String get statusActive => 'Active';

  @override
  String get statusTerminated => 'Terminated';

  @override
  String get statusExpired => 'Expired';
}
