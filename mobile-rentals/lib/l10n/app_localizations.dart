import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_am.dart';
import 'app_localizations_en.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('am'),
    Locale('en'),
  ];

  /// No description provided for @navListings.
  ///
  /// In en, this message translates to:
  /// **'Listings'**
  String get navListings;

  /// No description provided for @navContracts.
  ///
  /// In en, this message translates to:
  /// **'Contracts'**
  String get navContracts;

  /// No description provided for @navIndex.
  ///
  /// In en, this message translates to:
  /// **'Index'**
  String get navIndex;

  /// No description provided for @navProfile.
  ///
  /// In en, this message translates to:
  /// **'Profile'**
  String get navProfile;

  /// No description provided for @navBrowse.
  ///
  /// In en, this message translates to:
  /// **'Browse'**
  String get navBrowse;

  /// No description provided for @navApplications.
  ///
  /// In en, this message translates to:
  /// **'Applications'**
  String get navApplications;

  /// No description provided for @fieldEmail.
  ///
  /// In en, this message translates to:
  /// **'Email'**
  String get fieldEmail;

  /// No description provided for @fieldPassword.
  ///
  /// In en, this message translates to:
  /// **'Password'**
  String get fieldPassword;

  /// No description provided for @fieldFullName.
  ///
  /// In en, this message translates to:
  /// **'Full name'**
  String get fieldFullName;

  /// No description provided for @fieldPhone.
  ///
  /// In en, this message translates to:
  /// **'Phone (Ethiopian)'**
  String get fieldPhone;

  /// No description provided for @hintPhoneFormat.
  ///
  /// In en, this message translates to:
  /// **'09xxxxxxxx or +2519xxxxxxxx'**
  String get hintPhoneFormat;

  /// No description provided for @fieldSubCity.
  ///
  /// In en, this message translates to:
  /// **'Sub-city'**
  String get fieldSubCity;

  /// No description provided for @hintAnySubCity.
  ///
  /// In en, this message translates to:
  /// **'Any sub-city'**
  String get hintAnySubCity;

  /// No description provided for @fieldFaydaId.
  ///
  /// In en, this message translates to:
  /// **'Fayda ID number'**
  String get fieldFaydaId;

  /// No description provided for @hintFaydaId.
  ///
  /// In en, this message translates to:
  /// **'Your national digital ID'**
  String get hintFaydaId;

  /// No description provided for @hintPasswordRules.
  ///
  /// In en, this message translates to:
  /// **'8+ chars, an uppercase letter and a number'**
  String get hintPasswordRules;

  /// No description provided for @fieldAddress.
  ///
  /// In en, this message translates to:
  /// **'Address'**
  String get fieldAddress;

  /// No description provided for @hintAddress.
  ///
  /// In en, this message translates to:
  /// **'Building, street, area'**
  String get hintAddress;

  /// No description provided for @fieldType.
  ///
  /// In en, this message translates to:
  /// **'Type'**
  String get fieldType;

  /// No description provided for @fieldSubtype.
  ///
  /// In en, this message translates to:
  /// **'Subtype'**
  String get fieldSubtype;

  /// No description provided for @fieldArea.
  ///
  /// In en, this message translates to:
  /// **'Area (m2)'**
  String get fieldArea;

  /// No description provided for @fieldYearBuilt.
  ///
  /// In en, this message translates to:
  /// **'Year built'**
  String get fieldYearBuilt;

  /// No description provided for @hintOptional.
  ///
  /// In en, this message translates to:
  /// **'Optional'**
  String get hintOptional;

  /// No description provided for @fieldBedrooms.
  ///
  /// In en, this message translates to:
  /// **'Bedrooms'**
  String get fieldBedrooms;

  /// No description provided for @fieldBathrooms.
  ///
  /// In en, this message translates to:
  /// **'Bathrooms'**
  String get fieldBathrooms;

  /// No description provided for @fieldCondition.
  ///
  /// In en, this message translates to:
  /// **'Condition'**
  String get fieldCondition;

  /// No description provided for @hintSelectCondition.
  ///
  /// In en, this message translates to:
  /// **'Select condition'**
  String get hintSelectCondition;

  /// No description provided for @fieldOptionalMessage.
  ///
  /// In en, this message translates to:
  /// **'Optional message'**
  String get fieldOptionalMessage;

  /// No description provided for @hintReviewerMessage.
  ///
  /// In en, this message translates to:
  /// **'Anything the reviewer should know'**
  String get hintReviewerMessage;

  /// No description provided for @fieldMapPin.
  ///
  /// In en, this message translates to:
  /// **'Map pin (tap to place)'**
  String get fieldMapPin;

  /// No description provided for @fieldMessageToOwner.
  ///
  /// In en, this message translates to:
  /// **'Message to the owner (optional)'**
  String get fieldMessageToOwner;

  /// No description provided for @hintMessageToOwner.
  ///
  /// In en, this message translates to:
  /// **'Introduce yourself, move-in date, etc.'**
  String get hintMessageToOwner;

  /// No description provided for @fieldMaxRent.
  ///
  /// In en, this message translates to:
  /// **'Max rent (ETB/month)'**
  String get fieldMaxRent;

  /// No description provided for @hintNoLimit.
  ///
  /// In en, this message translates to:
  /// **'No limit'**
  String get hintNoLimit;

  /// No description provided for @labelPhone.
  ///
  /// In en, this message translates to:
  /// **'Phone'**
  String get labelPhone;

  /// No description provided for @labelFaydaId.
  ///
  /// In en, this message translates to:
  /// **'Fayda ID'**
  String get labelFaydaId;

  /// No description provided for @labelPropertyType.
  ///
  /// In en, this message translates to:
  /// **'Property type'**
  String get labelPropertyType;

  /// No description provided for @labelFloors.
  ///
  /// In en, this message translates to:
  /// **'Floors'**
  String get labelFloors;

  /// No description provided for @labelPublished.
  ///
  /// In en, this message translates to:
  /// **'Published'**
  String get labelPublished;

  /// No description provided for @labelAreaM2.
  ///
  /// In en, this message translates to:
  /// **'m2 area'**
  String get labelAreaM2;

  /// No description provided for @labelContract.
  ///
  /// In en, this message translates to:
  /// **'Contract'**
  String get labelContract;

  /// No description provided for @labelMonthlyRent.
  ///
  /// In en, this message translates to:
  /// **'Monthly rent'**
  String get labelMonthlyRent;

  /// No description provided for @labelTerm.
  ///
  /// In en, this message translates to:
  /// **'Term'**
  String get labelTerm;

  /// No description provided for @labelDeposit.
  ///
  /// In en, this message translates to:
  /// **'Deposit'**
  String get labelDeposit;

  /// No description provided for @labelDepositReceipt.
  ///
  /// In en, this message translates to:
  /// **'Deposit receipt'**
  String get labelDepositReceipt;

  /// No description provided for @labelYourOffer.
  ///
  /// In en, this message translates to:
  /// **'Your offer'**
  String get labelYourOffer;

  /// No description provided for @labelOffer.
  ///
  /// In en, this message translates to:
  /// **'Offer'**
  String get labelOffer;

  /// No description provided for @labelLimitReached.
  ///
  /// In en, this message translates to:
  /// **'Limit reached'**
  String get labelLimitReached;

  /// No description provided for @labelAny.
  ///
  /// In en, this message translates to:
  /// **'Any'**
  String get labelAny;

  /// No description provided for @actionSignIn.
  ///
  /// In en, this message translates to:
  /// **'Sign in'**
  String get actionSignIn;

  /// No description provided for @actionCancel.
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get actionCancel;

  /// No description provided for @actionAccept.
  ///
  /// In en, this message translates to:
  /// **'Accept'**
  String get actionAccept;

  /// No description provided for @actionDecline.
  ///
  /// In en, this message translates to:
  /// **'Decline'**
  String get actionDecline;

  /// No description provided for @actionDone.
  ///
  /// In en, this message translates to:
  /// **'Done'**
  String get actionDone;

  /// No description provided for @actionRemove.
  ///
  /// In en, this message translates to:
  /// **'Remove'**
  String get actionRemove;

  /// No description provided for @actionAddPhoto.
  ///
  /// In en, this message translates to:
  /// **'Add photo'**
  String get actionAddPhoto;

  /// No description provided for @actionAddShort.
  ///
  /// In en, this message translates to:
  /// **'Add'**
  String get actionAddShort;

  /// No description provided for @actionChooseFromGallery.
  ///
  /// In en, this message translates to:
  /// **'Choose from gallery'**
  String get actionChooseFromGallery;

  /// No description provided for @actionTakePhoto.
  ///
  /// In en, this message translates to:
  /// **'Take a photo'**
  String get actionTakePhoto;

  /// No description provided for @actionManagePhotos.
  ///
  /// In en, this message translates to:
  /// **'Manage photos'**
  String get actionManagePhotos;

  /// No description provided for @actionAgreement.
  ///
  /// In en, this message translates to:
  /// **'Agreement'**
  String get actionAgreement;

  /// No description provided for @preparingEllipsis.
  ///
  /// In en, this message translates to:
  /// **'Preparing...'**
  String get preparingEllipsis;

  /// No description provided for @actionViewApplications.
  ///
  /// In en, this message translates to:
  /// **'View applications'**
  String get actionViewApplications;

  /// No description provided for @actionRegisterProperty.
  ///
  /// In en, this message translates to:
  /// **'Register a property'**
  String get actionRegisterProperty;

  /// No description provided for @actionSubmitForReview.
  ///
  /// In en, this message translates to:
  /// **'Submit for review'**
  String get actionSubmitForReview;

  /// No description provided for @actionSubmitApplication.
  ///
  /// In en, this message translates to:
  /// **'Submit application'**
  String get actionSubmitApplication;

  /// No description provided for @actionApply.
  ///
  /// In en, this message translates to:
  /// **'Apply'**
  String get actionApply;

  /// No description provided for @actionClearFilters.
  ///
  /// In en, this message translates to:
  /// **'Clear filters'**
  String get actionClearFilters;

  /// No description provided for @actionResetFilters.
  ///
  /// In en, this message translates to:
  /// **'Reset filters'**
  String get actionResetFilters;

  /// No description provided for @actionShowResults.
  ///
  /// In en, this message translates to:
  /// **'Show results'**
  String get actionShowResults;

  /// No description provided for @actionDownloadContractPdf.
  ///
  /// In en, this message translates to:
  /// **'Download contract PDF'**
  String get actionDownloadContractPdf;

  /// No description provided for @preparingPdfEllipsis.
  ///
  /// In en, this message translates to:
  /// **'Preparing PDF...'**
  String get preparingPdfEllipsis;

  /// No description provided for @actionSignOut.
  ///
  /// In en, this message translates to:
  /// **'Sign out'**
  String get actionSignOut;

  /// No description provided for @actionTryAgain.
  ///
  /// In en, this message translates to:
  /// **'Try again'**
  String get actionTryAgain;

  /// No description provided for @actionCreateAccountShort.
  ///
  /// In en, this message translates to:
  /// **'Create account'**
  String get actionCreateAccountShort;

  /// No description provided for @welcomeCreateAccountCta.
  ///
  /// In en, this message translates to:
  /// **'Create an account'**
  String get welcomeCreateAccountCta;

  /// No description provided for @authAlreadyHaveAccount.
  ///
  /// In en, this message translates to:
  /// **'I already have an account'**
  String get authAlreadyHaveAccount;

  /// No description provided for @loginNewHerePrefix.
  ///
  /// In en, this message translates to:
  /// **'New here?'**
  String get loginNewHerePrefix;

  /// No description provided for @validationFullName.
  ///
  /// In en, this message translates to:
  /// **'Enter your full name.'**
  String get validationFullName;

  /// No description provided for @validationEmail.
  ///
  /// In en, this message translates to:
  /// **'Enter a valid email address.'**
  String get validationEmail;

  /// No description provided for @validationPhone.
  ///
  /// In en, this message translates to:
  /// **'Enter your phone number.'**
  String get validationPhone;

  /// No description provided for @validationFaydaId.
  ///
  /// In en, this message translates to:
  /// **'Enter your Fayda ID number.'**
  String get validationFaydaId;

  /// No description provided for @validationPasswordLength.
  ///
  /// In en, this message translates to:
  /// **'Password must be at least 8 characters.'**
  String get validationPasswordLength;

  /// No description provided for @validationPasswordUppercase.
  ///
  /// In en, this message translates to:
  /// **'Password needs an uppercase letter.'**
  String get validationPasswordUppercase;

  /// No description provided for @validationPasswordNumber.
  ///
  /// In en, this message translates to:
  /// **'Password needs a number.'**
  String get validationPasswordNumber;

  /// No description provided for @validationAddress.
  ///
  /// In en, this message translates to:
  /// **'Enter the full property address (at least 5 characters).'**
  String get validationAddress;

  /// No description provided for @validationArea.
  ///
  /// In en, this message translates to:
  /// **'Enter the area in square metres.'**
  String get validationArea;

  /// No description provided for @validationPhotoLimit.
  ///
  /// In en, this message translates to:
  /// **'A property may have at most {max} photos.'**
  String validationPhotoLimit(int max);

  /// No description provided for @onePhotoOversized.
  ///
  /// In en, this message translates to:
  /// **'One photo was over {mb}MB and was not added.'**
  String onePhotoOversized(int mb);

  /// No description provided for @multiplePhotosOversized.
  ///
  /// In en, this message translates to:
  /// **'{count} photos were over {mb}MB and were not added.'**
  String multiplePhotosOversized(int count, int mb);

  /// No description provided for @photosPartiallyAdded.
  ///
  /// In en, this message translates to:
  /// **'Only the first {remaining} photos were added ({max} max).'**
  String photosPartiallyAdded(int remaining, int max);

  /// No description provided for @screenTitleApplications.
  ///
  /// In en, this message translates to:
  /// **'Applications'**
  String get screenTitleApplications;

  /// No description provided for @screenTitleMyListings.
  ///
  /// In en, this message translates to:
  /// **'My listings'**
  String get screenTitleMyListings;

  /// No description provided for @screenSubtitleMyListings.
  ///
  /// In en, this message translates to:
  /// **'Properties you have put up for rent'**
  String get screenSubtitleMyListings;

  /// No description provided for @screenTitlePhotos.
  ///
  /// In en, this message translates to:
  /// **'Photos'**
  String get screenTitlePhotos;

  /// No description provided for @screenTitleRegisterProperty.
  ///
  /// In en, this message translates to:
  /// **'Register a property'**
  String get screenTitleRegisterProperty;

  /// No description provided for @screenTitleFindHome.
  ///
  /// In en, this message translates to:
  /// **'Find a home'**
  String get screenTitleFindHome;

  /// No description provided for @screenSubtitleFindHome.
  ///
  /// In en, this message translates to:
  /// **'Verified listings across Addis Ababa'**
  String get screenSubtitleFindHome;

  /// No description provided for @screenTitleAbout.
  ///
  /// In en, this message translates to:
  /// **'About & the law'**
  String get screenTitleAbout;

  /// No description provided for @screenTitleActivity.
  ///
  /// In en, this message translates to:
  /// **'Activity'**
  String get screenTitleActivity;

  /// No description provided for @screenTitleMyContracts.
  ///
  /// In en, this message translates to:
  /// **'My contracts'**
  String get screenTitleMyContracts;

  /// No description provided for @screenSubtitleMyContracts.
  ///
  /// In en, this message translates to:
  /// **'Registered tenancy agreements'**
  String get screenSubtitleMyContracts;

  /// No description provided for @screenTitleMyApplications.
  ///
  /// In en, this message translates to:
  /// **'My applications'**
  String get screenTitleMyApplications;

  /// No description provided for @screenSubtitleMyApplications.
  ///
  /// In en, this message translates to:
  /// **'Every offer you have made'**
  String get screenSubtitleMyApplications;

  /// No description provided for @screenTitleRentIndex.
  ///
  /// In en, this message translates to:
  /// **'Rent index'**
  String get screenTitleRentIndex;

  /// No description provided for @screenSubtitleRentIndex.
  ///
  /// In en, this message translates to:
  /// **'Median registered rents by sub-city'**
  String get screenSubtitleRentIndex;

  /// No description provided for @loginSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Sign in to your registry account'**
  String get loginSubtitle;

  /// No description provided for @signupSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Create your registry account'**
  String get signupSubtitle;

  /// No description provided for @signupTypeRenterTitle.
  ///
  /// In en, this message translates to:
  /// **'Rent a home'**
  String get signupTypeRenterTitle;

  /// No description provided for @signupTypeOwnerTitle.
  ///
  /// In en, this message translates to:
  /// **'List a property'**
  String get signupTypeOwnerTitle;

  /// No description provided for @signupOwnerNote.
  ///
  /// In en, this message translates to:
  /// **'Owner accounts are verified by a rental officer before a listing can be published. You can prepare listings right away.'**
  String get signupOwnerNote;

  /// No description provided for @welcomeAgency.
  ///
  /// In en, this message translates to:
  /// **'Addis Ababa Housing Administration'**
  String get welcomeAgency;

  /// No description provided for @welcomeHero.
  ///
  /// In en, this message translates to:
  /// **'Rent a home at an honest, valuation-certified price. Every listing and contract is registered with the government.'**
  String get welcomeHero;

  /// No description provided for @welcomePoint1Title.
  ///
  /// In en, this message translates to:
  /// **'Certified prices'**
  String get welcomePoint1Title;

  /// No description provided for @welcomePoint1Body.
  ///
  /// In en, this message translates to:
  /// **'A published band from an official valuation, not a broker guess.'**
  String get welcomePoint1Body;

  /// No description provided for @welcomePoint2Title.
  ///
  /// In en, this message translates to:
  /// **'Registered contracts'**
  String get welcomePoint2Title;

  /// No description provided for @welcomePoint2Body.
  ///
  /// In en, this message translates to:
  /// **'Written and registered under Proclamation 1320/2024.'**
  String get welcomePoint2Body;

  /// No description provided for @welcomePoint3Title.
  ///
  /// In en, this message translates to:
  /// **'A public rent index'**
  String get welcomePoint3Title;

  /// No description provided for @welcomePoint3Body.
  ///
  /// In en, this message translates to:
  /// **'See the median rent per sub-city before you decide.'**
  String get welcomePoint3Body;

  /// No description provided for @welcomeHeroCaption.
  ///
  /// In en, this message translates to:
  /// **'28,000 ETB/mo · Bole'**
  String get welcomeHeroCaption;

  /// No description provided for @splashTagline.
  ///
  /// In en, this message translates to:
  /// **'Government-mediated rental registry'**
  String get splashTagline;

  /// No description provided for @emptyNoApplicationsTitle.
  ///
  /// In en, this message translates to:
  /// **'No applications yet'**
  String get emptyNoApplicationsTitle;

  /// No description provided for @ownerEmptyApplicationsMessage.
  ///
  /// In en, this message translates to:
  /// **'When renters apply within your band, their offers appear here for you to accept or decline.'**
  String get ownerEmptyApplicationsMessage;

  /// No description provided for @renterEmptyApplicationsMessage.
  ///
  /// In en, this message translates to:
  /// **'When you apply to a listing, it will appear here so you can track the owner\'s decision.'**
  String get renterEmptyApplicationsMessage;

  /// No description provided for @emptyNoListingsTitle.
  ///
  /// In en, this message translates to:
  /// **'List your first property'**
  String get emptyNoListingsTitle;

  /// No description provided for @emptyNoListingsMessage.
  ///
  /// In en, this message translates to:
  /// **'Register a property and we will suggest an honest rent band from an official valuation. An officer reviews it before it goes public.'**
  String get emptyNoListingsMessage;

  /// No description provided for @emptyNoPhotosTitle.
  ///
  /// In en, this message translates to:
  /// **'No photos yet'**
  String get emptyNoPhotosTitle;

  /// No description provided for @emptyNoPhotosMessage.
  ///
  /// In en, this message translates to:
  /// **'Add up to {max} real photos so renters see the actual unit, not a placeholder.'**
  String emptyNoPhotosMessage(int max);

  /// No description provided for @emptyNoMatchesTitle.
  ///
  /// In en, this message translates to:
  /// **'No matches yet'**
  String get emptyNoMatchesTitle;

  /// No description provided for @emptyNoMatchesFilteredMessage.
  ///
  /// In en, this message translates to:
  /// **'No published listings fit these filters. Try widening your search.'**
  String get emptyNoMatchesFilteredMessage;

  /// No description provided for @emptyNoMatchesMessage.
  ///
  /// In en, this message translates to:
  /// **'There are no published listings right now. Check back soon.'**
  String get emptyNoMatchesMessage;

  /// No description provided for @emptyActivityTitle.
  ///
  /// In en, this message translates to:
  /// **'Nothing new'**
  String get emptyActivityTitle;

  /// No description provided for @emptyActivityMessage.
  ///
  /// In en, this message translates to:
  /// **'Status changes on your applications and contracts show up here. This updates automatically while the app is open.'**
  String get emptyActivityMessage;

  /// No description provided for @emptyNoContractsTitle.
  ///
  /// In en, this message translates to:
  /// **'No contracts yet'**
  String get emptyNoContractsTitle;

  /// No description provided for @emptyNoContractsMessage.
  ///
  /// In en, this message translates to:
  /// **'Once an application is accepted and an officer registers the tenancy, your contract will appear here with its PDF.'**
  String get emptyNoContractsMessage;

  /// No description provided for @emptyIndexTitle.
  ///
  /// In en, this message translates to:
  /// **'Index still building'**
  String get emptyIndexTitle;

  /// No description provided for @emptyIndexMessage.
  ///
  /// In en, this message translates to:
  /// **'The index publishes a median only where enough contracts have been registered. As the registry grows, medians per sub-city appear here.'**
  String get emptyIndexMessage;

  /// No description provided for @errorLoadApplications.
  ///
  /// In en, this message translates to:
  /// **'Could not load applications.'**
  String get errorLoadApplications;

  /// No description provided for @errorLoadListings.
  ///
  /// In en, this message translates to:
  /// **'Could not load listings.'**
  String get errorLoadListings;

  /// No description provided for @errorLoadPhotos.
  ///
  /// In en, this message translates to:
  /// **'Could not load photos.'**
  String get errorLoadPhotos;

  /// No description provided for @errorLoadListing.
  ///
  /// In en, this message translates to:
  /// **'Could not load this listing.'**
  String get errorLoadListing;

  /// No description provided for @errorLoadContracts.
  ///
  /// In en, this message translates to:
  /// **'Could not load contracts.'**
  String get errorLoadContracts;

  /// No description provided for @errorLoadIndex.
  ///
  /// In en, this message translates to:
  /// **'Could not load the index.'**
  String get errorLoadIndex;

  /// No description provided for @dialogAcceptTitle.
  ///
  /// In en, this message translates to:
  /// **'Accept this applicant?'**
  String get dialogAcceptTitle;

  /// No description provided for @dialogAcceptContent.
  ///
  /// In en, this message translates to:
  /// **'Accepting {name} at {rent} marks the listing as rented and declines the others. A rental officer then registers the contract.'**
  String dialogAcceptContent(String name, String rent);

  /// No description provided for @defaultRenterName.
  ///
  /// In en, this message translates to:
  /// **'this renter'**
  String get defaultRenterName;

  /// No description provided for @defaultApplicantLabel.
  ///
  /// In en, this message translates to:
  /// **'Applicant'**
  String get defaultApplicantLabel;

  /// No description provided for @dialogRemovePhotoTitle.
  ///
  /// In en, this message translates to:
  /// **'Remove this photo?'**
  String get dialogRemovePhotoTitle;

  /// No description provided for @dialogCannotUndo.
  ///
  /// In en, this message translates to:
  /// **'This cannot be undone.'**
  String get dialogCannotUndo;

  /// No description provided for @snackApplicationAccepted.
  ///
  /// In en, this message translates to:
  /// **'Accepted. An officer will register the contract.'**
  String get snackApplicationAccepted;

  /// No description provided for @snackApplicationDeclined.
  ///
  /// In en, this message translates to:
  /// **'Application declined.'**
  String get snackApplicationDeclined;

  /// No description provided for @snackApplicationSent.
  ///
  /// In en, this message translates to:
  /// **'Application sent at {price}. Track it under Applications.'**
  String snackApplicationSent(String price);

  /// No description provided for @verificationPendingTitle.
  ///
  /// In en, this message translates to:
  /// **'Verification pending'**
  String get verificationPendingTitle;

  /// No description provided for @verificationPendingMessage.
  ///
  /// In en, this message translates to:
  /// **'A rental officer is reviewing your Fayda ID. You can prepare listings now, but they publish only after you are verified.'**
  String get verificationPendingMessage;

  /// No description provided for @officerNoteLabel.
  ///
  /// In en, this message translates to:
  /// **'Officer note: {reason}'**
  String officerNoteLabel(String reason);

  /// No description provided for @publishedOnLabel.
  ///
  /// In en, this message translates to:
  /// **'Published {date}'**
  String publishedOnLabel(String date);

  /// No description provided for @createdOnLabel.
  ///
  /// In en, this message translates to:
  /// **'Created {date}'**
  String createdOnLabel(String date);

  /// No description provided for @bandRangeLabel.
  ///
  /// In en, this message translates to:
  /// **'Band {min} - {max}'**
  String bandRangeLabel(String min, String max);

  /// No description provided for @resultSubmittedTitle.
  ///
  /// In en, this message translates to:
  /// **'Submitted for review'**
  String get resultSubmittedTitle;

  /// No description provided for @resultSubmittedMessage.
  ///
  /// In en, this message translates to:
  /// **'A rental officer will verify the details and publish your listing at the band below.'**
  String get resultSubmittedMessage;

  /// No description provided for @onePhotoUploadFailed.
  ///
  /// In en, this message translates to:
  /// **'One photo could not be uploaded. Add it from Manage photos on this listing.'**
  String get onePhotoUploadFailed;

  /// No description provided for @multiplePhotosUploadFailed.
  ///
  /// In en, this message translates to:
  /// **'{count} photos could not be uploaded. Add them from Manage photos on this listing.'**
  String multiplePhotosUploadFailed(int count);

  /// No description provided for @sectionLocation.
  ///
  /// In en, this message translates to:
  /// **'Location'**
  String get sectionLocation;

  /// No description provided for @sectionProperty.
  ///
  /// In en, this message translates to:
  /// **'Property'**
  String get sectionProperty;

  /// No description provided for @sectionPhotos.
  ///
  /// In en, this message translates to:
  /// **'Photos'**
  String get sectionPhotos;

  /// No description provided for @sectionNoteToOfficer.
  ///
  /// In en, this message translates to:
  /// **'Note to the officer'**
  String get sectionNoteToOfficer;

  /// No description provided for @photoUploadHint.
  ///
  /// In en, this message translates to:
  /// **'Photos upload to the registry when you submit. JPG, PNG or WEBP, up to {mb}MB each, {max} max.'**
  String photoUploadHint(int mb, int max);

  /// No description provided for @applySheetTitle.
  ///
  /// In en, this message translates to:
  /// **'Apply to rent'**
  String get applySheetTitle;

  /// No description provided for @applyWithinBand.
  ///
  /// In en, this message translates to:
  /// **'Within the allowed band'**
  String get applyWithinBand;

  /// No description provided for @filterListingsLabel.
  ///
  /// In en, this message translates to:
  /// **'Filter listings'**
  String get filterListingsLabel;

  /// No description provided for @bedCount.
  ///
  /// In en, this message translates to:
  /// **'{n} bed'**
  String bedCount(int n);

  /// No description provided for @bathCount.
  ///
  /// In en, this message translates to:
  /// **'{n} bath'**
  String bathCount(int n);

  /// No description provided for @bedCountPlus.
  ///
  /// In en, this message translates to:
  /// **'{n}+'**
  String bedCountPlus(int n);

  /// No description provided for @maxRentSummary.
  ///
  /// In en, this message translates to:
  /// **'<= {price}'**
  String maxRentSummary(String price);

  /// No description provided for @filterSheetTitle.
  ///
  /// In en, this message translates to:
  /// **'Filter'**
  String get filterSheetTitle;

  /// No description provided for @mapPinMissingInfo.
  ///
  /// In en, this message translates to:
  /// **'{count} of {total} listings have no map pin yet and are shown only in the list.'**
  String mapPinMissingInfo(int count, int total);

  /// No description provided for @perMonthSuffix.
  ///
  /// In en, this message translates to:
  /// **'/month'**
  String get perMonthSuffix;

  /// No description provided for @perMonthSuffixShort.
  ///
  /// In en, this message translates to:
  /// **'/mo'**
  String get perMonthSuffixShort;

  /// No description provided for @bandPanelTitle.
  ///
  /// In en, this message translates to:
  /// **'Allowed rent band'**
  String get bandPanelTitle;

  /// No description provided for @bandPanelBody.
  ///
  /// In en, this message translates to:
  /// **'You can apply at any amount inside this band. Offers outside it are not accepted. The band is set from an official valuation, not a broker.'**
  String get bandPanelBody;

  /// No description provided for @propertyDetailsTitle.
  ///
  /// In en, this message translates to:
  /// **'Property details'**
  String get propertyDetailsTitle;

  /// No description provided for @chooseYourOfferLabel.
  ///
  /// In en, this message translates to:
  /// **'Choose your offer'**
  String get chooseYourOfferLabel;

  /// No description provided for @aboutIntro.
  ///
  /// In en, this message translates to:
  /// **'A government-mediated rental registry for Addis Ababa.'**
  String get aboutIntro;

  /// No description provided for @aboutLawTitle.
  ///
  /// In en, this message translates to:
  /// **'The law: Proclamation 1320/2024'**
  String get aboutLawTitle;

  /// No description provided for @aboutLawBody.
  ///
  /// In en, this message translates to:
  /// **'Ethiopia\'s Rent Control and Administration Proclamation requires residential rental contracts to be written and registered with the district housing administration. Rent increases are capped, and Addis Ababa set the ceiling at 11.5% for 2026/27. This app is the digital way to meet that mandate.'**
  String get aboutLawBody;

  /// No description provided for @aboutCertifiedTitle.
  ///
  /// In en, this message translates to:
  /// **'Certified prices, not broker guesses'**
  String get aboutCertifiedTitle;

  /// No description provided for @aboutCertifiedBody.
  ///
  /// In en, this message translates to:
  /// **'Every listing carries a rent band from an official valuation. You apply at any amount inside the band; owners choose a tenant, not a price war. There is no bidding.'**
  String get aboutCertifiedBody;

  /// No description provided for @aboutContractsBody.
  ///
  /// In en, this message translates to:
  /// **'When an owner accepts you, a rental officer registers the tenancy and issues a contract with a public contract number. The contract becomes active once your deposit receipt is recorded at the administration.'**
  String get aboutContractsBody;

  /// No description provided for @aboutDataTitle.
  ///
  /// In en, this message translates to:
  /// **'Your data'**
  String get aboutDataTitle;

  /// No description provided for @aboutDataBody.
  ///
  /// In en, this message translates to:
  /// **'Your Fayda ID and phone are used to verify you and appear only on your own contracts, never on public listings. Officers verify owner accounts before a listing can be published.'**
  String get aboutDataBody;

  /// No description provided for @aboutMissingTitle.
  ///
  /// In en, this message translates to:
  /// **'What is not here yet'**
  String get aboutMissingTitle;

  /// No description provided for @aboutMissingBody.
  ///
  /// In en, this message translates to:
  /// **'Deposits are recorded, not held in custody, in this version. There is no in-app chat; contact details are on the registered contract. Photo upload and Amharic are on the way.'**
  String get aboutMissingBody;

  /// No description provided for @aboutFooter.
  ///
  /// In en, this message translates to:
  /// **'Operated with the Addis Ababa Housing Administration'**
  String get aboutFooter;

  /// No description provided for @aboutSublabel.
  ///
  /// In en, this message translates to:
  /// **'Proclamation 1320/2024 explained'**
  String get aboutSublabel;

  /// No description provided for @activityApplicationLabel.
  ///
  /// In en, this message translates to:
  /// **'Application · {address}'**
  String activityApplicationLabel(String address);

  /// No description provided for @activityContractLabel.
  ///
  /// In en, this message translates to:
  /// **'Contract · {contractNo}'**
  String activityContractLabel(String contractNo);

  /// No description provided for @termRangeLabel.
  ///
  /// In en, this message translates to:
  /// **'{start}  ->  {end}'**
  String termRangeLabel(String start, String end);

  /// No description provided for @depositRecorded.
  ///
  /// In en, this message translates to:
  /// **'Recorded'**
  String get depositRecorded;

  /// No description provided for @depositAwaiting.
  ///
  /// In en, this message translates to:
  /// **'Awaiting record'**
  String get depositAwaiting;

  /// No description provided for @contractActivatesNote.
  ///
  /// In en, this message translates to:
  /// **'This contract activates once the officer records your deposit receipt at the housing administration.'**
  String get contractActivatesNote;

  /// No description provided for @defaultListingLabel.
  ///
  /// In en, this message translates to:
  /// **'Listing {id}'**
  String defaultListingLabel(String id);

  /// No description provided for @appliedOnLabel.
  ///
  /// In en, this message translates to:
  /// **'Applied {date}'**
  String appliedOnLabel(String date);

  /// No description provided for @roleOwner.
  ///
  /// In en, this message translates to:
  /// **'Property owner'**
  String get roleOwner;

  /// No description provided for @roleRenter.
  ///
  /// In en, this message translates to:
  /// **'Renter'**
  String get roleRenter;

  /// No description provided for @roleOfficer.
  ///
  /// In en, this message translates to:
  /// **'Rental officer'**
  String get roleOfficer;

  /// No description provided for @roleCitizen.
  ///
  /// In en, this message translates to:
  /// **'Citizen'**
  String get roleCitizen;

  /// No description provided for @defaultAccountName.
  ///
  /// In en, this message translates to:
  /// **'Your account'**
  String get defaultAccountName;

  /// No description provided for @statusVerified.
  ///
  /// In en, this message translates to:
  /// **'Verified'**
  String get statusVerified;

  /// No description provided for @statusVerificationPending.
  ///
  /// In en, this message translates to:
  /// **'Pending'**
  String get statusVerificationPending;

  /// No description provided for @settingsLanguageLabel.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get settingsLanguageLabel;

  /// No description provided for @settingsLanguageSublabel.
  ///
  /// In en, this message translates to:
  /// **'Choose the app language'**
  String get settingsLanguageSublabel;

  /// No description provided for @languageEnglish.
  ///
  /// In en, this message translates to:
  /// **'English'**
  String get languageEnglish;

  /// No description provided for @languageAmharic.
  ///
  /// In en, this message translates to:
  /// **'አማርኛ'**
  String get languageAmharic;

  /// No description provided for @indexIntroText.
  ///
  /// In en, this message translates to:
  /// **'Medians from registered tenancy contracts for {period}. Low-sample cells are hidden, so what you see is real.'**
  String indexIntroText(String period);

  /// No description provided for @sampleSizeLabel.
  ///
  /// In en, this message translates to:
  /// **'n={n}'**
  String sampleSizeLabel(int n);

  /// No description provided for @bandSpreadLabel.
  ///
  /// In en, this message translates to:
  /// **'{percent}% band'**
  String bandSpreadLabel(int percent);

  /// No description provided for @suggestedPriceLabel.
  ///
  /// In en, this message translates to:
  /// **'Suggested {price}'**
  String suggestedPriceLabel(String price);

  /// No description provided for @photoPendingLabel.
  ///
  /// In en, this message translates to:
  /// **'Photo pending'**
  String get photoPendingLabel;

  /// No description provided for @locationNotPinnedLabel.
  ///
  /// In en, this message translates to:
  /// **'Location not pinned'**
  String get locationNotPinnedLabel;

  /// No description provided for @certifiedBadgeLabel.
  ///
  /// In en, this message translates to:
  /// **'Certified'**
  String get certifiedBadgeLabel;

  /// No description provided for @statusPending.
  ///
  /// In en, this message translates to:
  /// **'Pending'**
  String get statusPending;

  /// No description provided for @statusAccepted.
  ///
  /// In en, this message translates to:
  /// **'Accepted'**
  String get statusAccepted;

  /// No description provided for @statusRejected.
  ///
  /// In en, this message translates to:
  /// **'Not selected'**
  String get statusRejected;

  /// No description provided for @statusWithdrawn.
  ///
  /// In en, this message translates to:
  /// **'Withdrawn'**
  String get statusWithdrawn;

  /// No description provided for @statusDraft.
  ///
  /// In en, this message translates to:
  /// **'Draft'**
  String get statusDraft;

  /// No description provided for @statusPendingReview.
  ///
  /// In en, this message translates to:
  /// **'Under review'**
  String get statusPendingReview;

  /// No description provided for @statusPublished.
  ///
  /// In en, this message translates to:
  /// **'Published'**
  String get statusPublished;

  /// No description provided for @statusRented.
  ///
  /// In en, this message translates to:
  /// **'Rented'**
  String get statusRented;

  /// No description provided for @statusActive.
  ///
  /// In en, this message translates to:
  /// **'Active'**
  String get statusActive;

  /// No description provided for @statusTerminated.
  ///
  /// In en, this message translates to:
  /// **'Terminated'**
  String get statusTerminated;

  /// No description provided for @statusExpired.
  ///
  /// In en, this message translates to:
  /// **'Expired'**
  String get statusExpired;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['am', 'en'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'am':
      return AppLocalizationsAm();
    case 'en':
      return AppLocalizationsEn();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
